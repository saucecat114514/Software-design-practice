# -*- coding: utf-8 -*-
"""A5 需求验证运行器：程序确定性检查 + 逐子系统 LLM 语义验证 → 验证报告。
用法：python run_verification.py [all|prog|llm]
  prog  仅程序检查（REQ覆盖率/模糊词/FR编号与交叉引用），快、确定性
  llm   仅逐子系统 LLM 语义验证
  all   两者 + 写出 需求验证报告-v1.0.md
输出：wiki/summaries/需求验证报告-v1.0.md
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
SUM = HERE.parents[1]                 # wiki/summaries
PARTS = SUM / "srs_parts"

import llm_config as L                # noqa: E402
import agent_verifier as A5           # noqa: E402

REQ_FILE = SUM / "需求清单-v1.0.md"
CCB_FILE = SUM / "CCB裁决记录-v1.0.md"
SRS_FILE = SUM / "SRS-初稿-v0.1.md"

SUBSYS = [
    (1, "招生与客户管理子系统", "课程顾问"),
    (2, "教务管理子系统", "教务老师"),
    (3, "财务管理子系统", "财务人员"),
    (4, "经营管理子系统", "校长"),
    (5, "系统管理子系统", "系统管理员"),
]

FUZZY = ["尽量", "尽可能", "通常", "一般情况下", "大概", "左右", "适当", "合理", "快速",
         "及时", "友好", "差不多", "比较", "经常", "视情况", "酌情", "适度", "尽快"]


def parse_sections(text):
    secs, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r'^##\s+(\S+)\s*$', line)
        if m and not line.startswith('###'):
            if cur:
                secs[cur] = "\n".join(buf)
            cur, buf = m.group(1), []
        elif cur is not None:
            buf.append(line)
    if cur:
        secs[cur] = "\n".join(buf)
    return secs


def prog_check():
    """程序确定性检查，返回 Markdown 文本。"""
    req_txt = REQ_FILE.read_text(encoding="utf-8")
    srs_txt = SRS_FILE.read_text(encoding="utf-8")
    out = ["## 一、程序确定性检查（A5 自动化）\n"]

    # 1) REQ 覆盖率
    all_req = sorted(set(re.findall(r'^###\s+(REQ-[A-Z]+-\d+)', req_txt, re.M)))
    cited = set(re.findall(r'REQ-[A-Z]+-\d+', srs_txt))
    uncovered = [r for r in all_req if r not in cited]
    out.append("### 1.1 需求覆盖率（REQ → SRS 追溯）")
    out.append(f"- 需求清单唯一 REQ 编号：**{len(all_req)}** 个（注：教务/财务/校长间存在同名编号复用，唯一编号数 < 125 条目数）。")
    out.append(f"- SRS 追溯字段引用到的 REQ 编号：**{len(cited & set(all_req))}** 个。")
    if uncovered:
        out.append(f"- ⚠ **未被 SRS 显式引用的 REQ（{len(uncovered)} 个）**：{', '.join(uncovered)}")
        out.append("  - 处置：逐一确认是否被某 FR 语义覆盖但漏写追溯，或确属遗漏需补 FR。")
    else:
        out.append("- ✔ 全部唯一 REQ 编号均被 SRS 追溯字段引用，无显式遗漏。")
    out.append("")

    # 2) 模糊词扫描
    out.append("### 1.2 模糊措辞扫描（IEEE 830 可验证性）")
    hits = []
    for i, line in enumerate(srs_txt.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("|---") or "禁用" in s or "禁止" in s or "模糊" in s:
            continue
        for w in FUZZY:
            if w in line:
                hits.append((i, w, s[:60]))
    if hits:
        out.append(f"- 命中疑似模糊词 **{len(hits)}** 处（已排除元描述行）：")
        for i, w, ctx in hits[:40]:
            out.append(f"  - 行 {i}「{w}」：{ctx}")
        if len(hits) > 40:
            out.append(f"  - …其余 {len(hits) - 40} 处见正文。")
        out.append("  - 处置：逐处判定——若可替换为量化阈值则改（如'及时'→'≤1分钟'），属固定术语/引用则保留。")
    else:
        out.append("- ✔ 未命中模糊词。")
    out.append("")

    # 3) FR/IFR 编号与交叉引用
    out.append("### 1.3 编号唯一性与交叉引用完整性")
    fr_defs = re.findall(r'^####\s+(FR-[A-Z]+-\d+)', srs_txt, re.M)
    ifr_defs = re.findall(r'^###\s+(IFR-[A-Z]+-\d+)', srs_txt, re.M)
    defs = set(fr_defs) | set(ifr_defs)
    dup = sorted({x for x in fr_defs if fr_defs.count(x) > 1})
    refs = set(re.findall(r'(?:FR|IFR)-[A-Z]+-\d+', srs_txt))
    broken = sorted(refs - defs)
    out.append(f"- FR 定义 **{len(fr_defs)}** 条、IFR 定义 **{len(ifr_defs)}** 条。")
    out.append(f"- 重复编号：{('⚠ ' + ', '.join(dup)) if dup else '✔ 无'}")
    if broken:
        out.append(f"- ⚠ **引用了但未定义的编号（{len(broken)}）**：{', '.join(broken)}")
        out.append("  - 处置：补定义、改为正确编号、或删除失效引用。")
    else:
        out.append("- ✔ 所有 FR/IFR 交叉引用均能解析到定义。")
    out.append("")
    return "\n".join(out)


def llm_check():
    """逐子系统 LLM 语义验证，返回 Markdown 文本。"""
    req_secs = parse_sections(REQ_FILE.read_text(encoding="utf-8"))
    ccb = CCB_FILE.read_text(encoding="utf-8")
    out = ["## 二、逐子系统语义验证（A5 智能体）\n"]
    for idx, name, sec in SUBSYS:
        fr_part = PARTS / f"03_fr_{idx}_{sec}.md"
        if not fr_part.exists():
            out.append(f"### {name}：⚠ 缺 FR 分章文件 {fr_part.name}\n")
            continue
        print(f"[验证] {name}")
        user = (f"=== SRS·{name} 功能需求章节 ===\n{fr_part.read_text(encoding='utf-8')}\n\n"
                f"=== 对应需求清单 REQ ===\n{req_secs.get(sec, '')}\n\n"
                f"=== CCB 裁决记录 ===\n{ccb}")
        res = L.chat_complete(
            [{"role": "system", "content": A5.verify_prompt(name)},
             {"role": "user", "content": user}],
            temperature=0.3, max_tokens=6000, max_rounds=8,
        )
        out.append(res.strip() + "\n")
    return "\n".join(out)


# ============ CCB 复核裁定的修订清单（A5 → SRS v0.2）============
CORRECTIONS = {
    1: """1. FR-TRIAL-001：将"数据实时性"业务规则补全为「P99≤3秒，目标≤1秒，>5秒触发告警」（CCB ISSUE-003）；异常处理中查询超时阈值统一改为 >5秒。
2. FR-TRIAL-005（试听候补）：候补排序规则纠正为「队列类型(付费试听高级队列 > 普通咨询队列) > 家长紧急程度(1天内 > 3天内 > 7天内 > 其他) > 进入时间」（CCB ISSUE-005/009）。把"加入候补的意向"拆为两步：①系统按报名来源自动判定队列类型；②顾问可手动标注"家长意向优先级(非此时段不可/优先此时段/任意时段均可)"作为独立的次要排序权重（REQ-TRIAL-008）。删除原"队列类型 > 家长意向优先级 > 进入时间"中以意向替代紧急度的表述。
3. FR-ORDER-003：删除"校长审批超时自动拒绝"分支；校长节点超时改为「工作日4h/非工作日8h，绝不自动通过也不自动拒绝，超时升级至值班校长，再超时升为最高级告警通知集团负责人」（CCB ISSUE-008）。代理人规则统一为「5分钟未处理提醒代理人；30分钟未处理转值班校长；代理人15分钟未处理则订单自动拒绝」。
4. FR-CRM-001：在"画像聚合内容"中补两项——「关联学员的试听上课记录(上课日期、任课老师、课堂表现、家长课后反馈)」「历次报价的完整方案(报价日期、课程包、价格、优惠方案、未成交原因)」；追溯字段补 REQ-CRM-004、REQ-CRM-005。
5. FR-CRM-002：撞单提示由"显示归属顾问姓名"改为「提示该客户已有归属顾问(姓名按配置脱敏展示)及最近跟进摘要」。
6. FR-ORDER-005：将"严禁任何线下收款"改为「严禁在顾问/教务端提供任何线下收款(现金/POS/个人转账)入口；线下拆分等操作仅限授权财务人员在后台模块执行」。
7. 模糊词量化：本章所有"X分钟内/X秒内"统一为"≤X分钟/≤X秒"；"5分钟内未处理""30分钟内未处理"改为"≤5分钟未处理""≥30分钟未处理"。""",
    2: """1. FR-ATT-002（迟到）：删除"迟到≤15分钟不扣课时"规则；改为「扣课时以是否到课为准：到课即按课程规则扣减整次课时，迟到仅记录迟到时长与状态(出勤-迟到)，不影响扣课时」（CCB ISSUE-010）。验收标准同步：模拟迟到10分钟签到，状态"出勤(迟到)"，正常扣减1课时、剩余课时减1。
2. FR-ATT-003（临时病假）：将"按可配置比例(默认50%)扣课时"改为「临时病假凭3个工作日内合规诊断证明，审批通过后免扣课时；无证明或未通过审批者按缺勤规则扣课时」（CCB ISSUE-006）。诊断证明时窗表述简化为"3个工作日内合规机构出具的诊断证明"，删除冗余的日期推断描述。普通请假(开课前>2小时提交不扣、≤2小时提交扣本次)保持不变。
3. FR-SCH-001：删除"参见 FR-SCH-006"悬空引用；把"缓冲时间默认5分钟、可按教室对配置"的配置逻辑明确为本 FR 自身职责（REQ-SCH-002），不再外引。
4. FR-RPT-001（教务报表）改名为 FR-TRP-001（标题与正文引用一并改）；教师维度报表明确每行显示"原定教师"与"实际上课教师"两列，代课时二者不同。修正"出勤节数、请假节数、缺勤节数、、剩余课时"的连续逗号笔误为"出勤节数、请假节数、缺勤节数、剩余课时"。
5. FR-REF-001（教务办理退费）改名为 FR-TREF-001（标题与正文引用一并改）；其退费审批中间档"按就高不就低原则"改为明确引用 CCB ISSUE-008 区间：「退费金额 >5000 且 ≤10000，或折扣 ≥85折 且 <9折，或课时>150 → 校长强制审批」。注意：应退金额公式「剩余正课课时 × 退费单价」保持不变（CCB ISSUE-007 赠课不折现，不得改为含赠课）。
6. FR-RSCH-001（调课）：业务流程补「系统于每日日切后自动生成上一日调课通知中仍未读的家长待办清单，推送至教务待办中心」（REQ-RSCH-003）。
7. FR-CLS-002（候补转正）：业务流程补「系统同步向教务老师推送待办，含候补学员信息与差价明细，教务老师可后台核验」（REQ-CLS-002）。
8. FR-MCAM-001（多校区）：业务流程补「支持'全集团/多校区汇总'视图，汇总展示所有授权校区的排课、考勤数据」（REQ-MCAM-001）。""",
    3: """1. FR-REF-003（审批退费）：把三级"绝不自动通过"从仅验收用例提升为明确写入业务规则；审批分档严格对齐 CCB ISSUE-008：一级「退费金额≤5000元 且 折扣≥9折 → 校区主管，30分钟超时自动通过并标异常通过抄送」；二级「>5000且≤10000元，或折扣≥85折且<9折 → 工作日4h/非工作日8h 超时自动通过」；三级「>10000元 或 折扣<85折 或 课时>150 → 校长强制审批，绝不自动通过」。补「代理人15分钟未处理则订单自动拒绝」。
2. FR-PAY-002（家长回填）：删除"收款人姓名"作为家长必填匹配要素，保留"学籍号 + 金额"匹配（REQ-PAY-002）。
3. FR-INV-001：保持定义。凡正文中引用的 FR-INV-003、FR-INV-004（发票红冲状态校验、发票状态标签）一律改为引用 FR-INV-001（处理发票），因为红冲状态校验与状态标签均由 FR-INV-001 覆盖；FR-REF-003 中"调用 FR-INV-003 强制校验发票红冲状态"改为"调用 FR-INV-001 强制校验发票红冲状态(已开票未红冲则阻断并引导红冲)"。
4. FR-RPT-001（财务·查看经营利润表）改名为 FR-FRP-001；FR-RPT-002（财务·欠费账龄）若存在改名为 FR-FRP-002，FR-RPT-003（财务·课程盈利）若存在改名为 FR-FRP-003，FR-RPT-004 改 FR-FRP-004（标题与正文引用一并改）。
5. FR-RECON-001：删除"手动拉取响应时间≤5秒"的强约束验收，改为「前端即时反馈'拉取任务已创建'」。
6. FR-PAY-003：把"我们将尽快核实"改为"财务人员将在1个工作日内完成核实"。
7. 折价系数默认1、发票审核阈值默认5000：在对应业务规则后加注"(默认值，可配置，待 CCB 正式确认)"。""",
    4: """1. FR-CAMPUS-001（分级审批与数据权限）：业务规则补「值班校长规则：审批超时30分钟，系统自动转交值班校长处理；值班校长为多校区共同上级，由系统管理员在配置中指定」；校长强制审批规则结尾补「若超时(工作日4h/非工作日8h)，系统绝不自动通过也不自动拒绝，而是升级为最高级告警，经统一通知中心通知集团负责人并在告警中心置顶」（CCB ISSUE-008）。把"配置生效回流"改为明确表述「配置保存成功提示；新规则立即对之后发起的申请生效，已发起审批不受影响」。
2. FR-APPROVAL-001（关键财务审批）：业务规则补「审批参数快照冻结规则：审批单发起时即按 FR-CAMPUS-001 规则生成参数快照并冻结；流程中的审批单始终按发起时快照执行，后台配置变更只对新发起申请生效」（CCB ISSUE-016）。
3. FR-FIN-003（日终对账）：把"所有资金变动操作即时触发一次增量对账"改为「所有资金变动操作(退费/补款/单边账认领)在≤1秒内触发一次增量对账任务，对账结果≤1分钟反映至看板与告警中心」。
4. FR-FIN-001（校长·查看实时课消与确认收入）改名为 FR-FMN-001（标题与正文引用一并改）。
5. FR-DASH-001、FR-CAMPUS-002：触发方式补出移动端首要地位——「用户访问移动端App首页(主视图)或PC后台首页」，并在 FR-CAMPUS-002 验收标准补「移动端适配按校区/班级排名列表，支持下滑刷新」。""",
    5: """1. FR-ORG-001（组织架构）：业务规则补层级约束「校区节点下可挂部门或班组，部门节点下可挂班组，班组为叶子节点」（REQ-ORG-001）。删除"数据权限基于组织节点向下覆盖：父节点角色可查看其下所有子节点数据"这一硬编码继承句——数据范围权限由 FR-ORG-002 的数据范围选项定义。
2. FR-ACC-002（权限模板/继承叠加）：验收标准补一条「用户权限列表界面，继承权限与自定义权限以不同颜色或标识明确区分，可验证」（REQ-ACC-003）。
3. 新增 FR-DR-003 备份数据安全管控（紧接 FR-DR 系列之后，字段格式与同章一致）：优先级 P0；参与角色 系统管理员/超级管理员；业务规则「备份文件以加密(非明文)形式存储；仅超级管理员可执行备份下载/恢复；对备份的任何访问/下载/恢复均生成独立审计日志」；验收标准可量化；追溯 REQ-DR-003。
4. FR-PAY-001（系统·处理支付异常与对账）改名为 FR-PAYIF-001（标题与正文引用一并改）；其中"单边账报表"全部改为"单边待认领账报表"（CCB ISSUE-020）；主动查单时限"24小时内"改为"重试全失败后立即启动，不晚于次日18:00日切前完成"（CCB ISSUE-014）。
5. 新增 FR-BIZ-003 规则变更的遗留数据处理（紧接 FR-BIZ-002 之后，字段格式一致）：优先级 P0；业务规则「业务规则变更以'业务单据提交时间'为切割点：提交时间在变更生效前的单据按旧规则计算，之后按新规则；处理中的审批/退费单按其发起时冻结的参数快照执行(呼应 CCB ISSUE-016)；例外调整需走日志+权限」；追溯 REQ-BIZ-003。
6. FR-SEC-002（安全策略/告警）：业务流程中删除把"对账异常"汇入本告警的表述——对账异常归 FR-PAYIF-001 集团集中告警(CCB ISSUE-018)，本处仅汇入"审批超时等业务异常 + 安全高危"；后置状态补「校区校长登录告警中心可查看本校区对账异常与审批异常告警，但不可处理或关闭(集团集中)」。
7. FR-BIZ-002（模拟试算）：把"试算结果与实际执行一致"的"一致"定义为「金额数值精确到分、规则引用一致、差异为0」，使之可测。""",
}


def revise():
    """据 CCB 修订清单逐子系统改写 FR 分章 → 覆盖写回 srs_parts。"""
    for idx, name, sec in SUBSYS:
        fr_part = PARTS / f"03_fr_{idx}_{sec}.md"
        if not fr_part.exists() or idx not in CORRECTIONS:
            continue
        print(f"[修订] {name}")
        res = L.chat_complete(
            [{"role": "system", "content": A5.revise_prompt(name, CORRECTIONS[idx])},
             {"role": "user", "content": fr_part.read_text(encoding="utf-8")}],
            temperature=0.2, max_tokens=8000, max_rounds=10,
        )
        res = res.strip()
        m = re.search(r'###\s+3\.1\.\d.*', res, re.S)
        out = (m.group(0) if m else res).strip() + "\n"
        fr_part.write_text(out, encoding="utf-8")
        print(f"        → {len(out)} 字")


def main(mode="all"):
    if mode == "revise":
        revise()
        print("完成。请重跑 run_srs.py assemble 重拼 SRS。")
        return
    parts = []
    head = ("# 需求验证报告 · v1.0（A5 交叉验证）\n\n"
            "> A5 需求验证智能体对 [[SRS-初稿-v0.1]] 做四维交叉验证：① 历史需求覆盖；② CCB 裁决一致性与越界；"
            "③ 涉众诉求保真（经 REQ 传递）；④ SRS 内部质量（模糊/可测/一致/交叉引用）。\n"
            "> 程序检查为确定性结论；语义验证由 DeepSeek 逐子系统给出。处置见文末第三节。"
            "见 [[需求清单-v1.0]]、[[CCB裁决记录-v1.0]]、[[00_项目总作战计划]]。\n\n---\n")
    parts.append(head)
    if mode in ("all", "prog"):
        print("[程序检查]")
        parts.append(prog_check())
    if mode in ("all", "llm"):
        parts.append(llm_check())
    report = "\n".join(parts)
    if mode == "all":
        (SUM / "需求验证报告-v1.0.md").write_text(report, encoding="utf-8")
        print("[写出] 需求验证报告-v1.0.md")
    else:
        # 预览模式：打印到 stdout（程序检查）或同样写文件
        (SUM / "需求验证报告-v1.0.md").write_text(report, encoding="utf-8")
        print("[写出] 需求验证报告-v1.0.md（部分模式）")
    print("完成。")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
