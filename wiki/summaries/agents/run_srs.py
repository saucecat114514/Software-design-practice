# -*- coding: utf-8 -*-
"""A4 SRS 运行器：需求清单 + CCB 裁决 + A3 用例 → 分章生成 → 拼装 SRS 初稿。
用法：python run_srs.py [all|intro|fr|nfr|data|assemble] [子系统序号...]
  intro    生成 §1 引言 + §2 总体描述
  fr [n..] 生成 §3.1.n 各子系统功能需求（不带序号=全部 5 个）
  nfr      生成 §3.2 IFR + §3.3 NFR
  data     生成 §3.4 数据需求
  assemble 仅用已生成的分章文件拼装最终 SRS（不调用模型）
分章文件落 wiki/summaries/srs_parts/*.md；最终 wiki/summaries/SRS-初稿-v0.1.md
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
PROJECT_ROOT = HERE.parents[3]
SUM = HERE.parents[1]                 # wiki/summaries
UML = SUM / "uml"
PARTS = SUM / "srs_parts"
PARTS.mkdir(exist_ok=True)

import llm_config as L                # noqa: E402
import agent_srs as A4                # noqa: E402

REQ_FILE = SUM / "需求清单-v1.0.md"
CCB_FILE = SUM / "CCB裁决记录-v1.0.md"

# 子系统：(序号, 子系统名, 需求清单章节名, uc 文件名)
SUBSYS = [
    (1, "招生与客户管理子系统", "课程顾问", "uc_1_课程顾问.puml"),
    (2, "教务管理子系统", "教务老师", "uc_2_教务老师.puml"),
    (3, "财务管理子系统", "财务人员", "uc_3_财务人员.puml"),
    (4, "经营管理子系统", "校长", "uc_4_校长.puml"),
    (5, "系统管理子系统", "系统管理员", "uc_5_系统管理员.puml"),
]


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


def usecase_anchor(puml_name):
    """从用例图 puml 抽出用例名清单，作为 FR 粒度锚点。"""
    p = UML / puml_name
    if not p.exists():
        return ""
    names = re.findall(r'usecase\s+"([^"]+)"', p.read_text(encoding="utf-8"))
    return "、".join(names)


def gen(system_prompt, user_content, fname, max_tokens=8000):
    out = L.chat_complete(
        [{"role": "system", "content": system_prompt},
         {"role": "user", "content": user_content}],
        temperature=0.5, max_tokens=max_tokens, max_rounds=10,
    )
    out = out.strip() + "\n"
    (PARTS / fname).write_text(out, encoding="utf-8")
    n = len(out.replace(" ", "").replace("\n", ""))
    print(f"  [写出] {fname}  约 {n} 字")
    return out


def main(mode="all"):
    secs = parse_sections(REQ_FILE.read_text(encoding="utf-8"))
    ccb = CCB_FILE.read_text(encoding="utf-8")
    full_req = REQ_FILE.read_text(encoding="utf-8")

    if mode in ("all", "intro"):
        print("[§1+§2 引言与总体描述]")
        gen(A4.intro_overall_prompt(),
            f"=== 需求清单（参考，用于范围与术语） ===\n{full_req}",
            "01_intro_overall.md", max_tokens=7000)

    if mode in ("all", "fr"):
        only = {int(a) for a in sys.argv[2:] if a.isdigit()} if mode == "fr" else set()
        for idx, name, sec, ucf in SUBSYS:
            if only and idx not in only:
                continue
            print(f"[§3.1.{idx} FR] {name}")
            anchor = usecase_anchor(ucf)
            user = (f"=== 一、{name} 的全部需求条目 ===\n{secs.get(sec, '')}\n\n"
                    f"=== 二、CCB 裁决记录（业务规则口径，须落进 FR 业务规则） ===\n{ccb}")
            gen(A4.fr_prompt(name, f"3.1.{idx}", "见用例锚点", anchor),
                user, f"03_fr_{idx}_{sec}.md", max_tokens=8000)

    if mode in ("all", "nfr"):
        print("[§3.2 IFR + §3.3 NFR]")
        gen(A4.ifr_nfr_prompt(),
            f"=== 全量需求清单（含 IFR/NFR 条目） ===\n{full_req}\n\n=== CCB 裁决 ===\n{ccb}",
            "04_ifr_nfr.md", max_tokens=8000)

    if mode in ("all", "data"):
        print("[§3.4 数据需求]")
        gen(A4.data_prompt(),
            f"=== 需求清单（参考实体与字段） ===\n{full_req}",
            "05_data.md", max_tokens=7000)

    if mode in ("all", "assemble"):
        assemble()
    print("完成。分章目录:", PARTS)


def assemble():
    """把分章文件 + 头部/§4/§5 拼成最终 SRS。"""
    def read(fname):
        p = PARTS / fname
        return p.read_text(encoding="utf-8").strip() if p.exists() else f"<!-- 缺章: {fname} -->"

    header = HEADER
    intro_overall = read("01_intro_overall.md")
    fr_parts = "\n\n".join(read(f"03_fr_{i}_{s}.md") for i, _, s, _ in SUBSYS)
    ifr_nfr = read("04_ifr_nfr.md")
    data = read("05_data.md")

    doc = "\n\n".join([
        header,
        intro_overall,
        "# 3 具体需求\n\n## 3.1 功能需求（FR）\n\n> 编号规则：FR-<模块缩写>-<三位序号>；优先级 P0(必实现)/P1(重要)/P2(次要)；每条可追溯到 REQ 与 A3 用例/活动图。",
        fr_parts,
        ifr_nfr,
        data,
        SEC4_CHANGE,
        SEC5_APPENDIX,
    ])
    out = SUM / "SRS-初稿-v0.1.md"
    out.write_text(doc + "\n", encoding="utf-8")
    n = len(doc.replace(" ", "").replace("\n", ""))
    print(f"[拼装] {out.name}  约 {n} 字（不含空白）")


# ============ 由 A4 直接编写的固定章节（头部/§4/§5）============
HEADER = """# 软件需求规格说明书（SRS）· 教育培训机构教务收费管理系统

| 项目项 | 内容 |
|---|---|
| 文档名称 | 软件需求规格说明书（SRS） |
| 项目名称 | 教育培训机构教务收费管理系统 |
| 项目编号 | EDU-SRS-2026 |
| 文档版本 | V0.1.0（初稿） |
| 基线版本 | （待 CCB 审批后定为 BL-YYYYMMDD-01） |
| 编制人 | A4 需求文档智能体（DeepSeek deepseek-v4-pro）/ 项目负责人审阅 |
| 编制日期 | 2026-06-21 |
| 审核人 | A5 需求验证智能体（待执行） |
| 批准人 | CCB（待审批） |
| 密级 | 内部 |

## 修订历史记录
| 版本号 | 修订日期 | 修订人 | 修订类型 | 修订内容简述 | 审批人 |
|---|---|---|---|---|---|
| V0.1.0 | 2026-06-21 | A4 | 新建 | 据需求清单 v1.0（125 REQ）+ CCB 裁决记录 v1.0（24 ISSUE 收口）+ A3 UML 模型，生成 SRS 初稿 | 待 CCB |

> 本 SRS 由需求工程流水线产出：A1 获取 → A2 分析 → A3 建模 → **A4 生成（本文档）** → A5 验证 → CCB 审批 → A6 基线。
> 上游产物：[[需求清单-v1.0]]、[[CCB裁决记录-v1.0]]、[[UML建模说明-v1.0]]、[[需求问题清单-v2.0]]。见 [[00_项目总作战计划]]。"""

SEC4_CHANGE = """# 4 需求基线与变更管理

## 4.1 需求基线定义
1. 基线版本格式：`BL-YYYYMMDD-NN`（YYYYMMDD=创立日期，NN=当日流水号，从 01 起）。
2. 初始基线：本 SRS 经 A5 验证、CCB 审批通过后，由 A6 基线智能体冻结为第一版正式基线 `BL-YYYYMMDD-01`，并同时生成需求溯源矩阵（RTM）。
3. 基线冻结：基线发布后，任何需求修改必须经下述变更流程，禁止私自修改；历史基线完整归档、不覆盖、不删除。

## 4.2 需求变更整体流程
```mermaid
flowchart LR
    A[变更需求获取<br/>AI涉众沟通 / 提交CR] --> B[变更需求分析<br/>质量分析+建模+SRS初稿+基线比对差异]
    B --> C{CCB 审核}
    C -- 不通过 --> E[关闭, 流程结束]
    C -- 退回修改 --> A
    C -- 通过 --> D[新基线创立<br/>生成RTM+新版基线, 保留历史基线]
```

## 4.3 变更详细流程（四阶段）
- **阶段一 变更需求获取**：① 涉众 AI 智能体（A1）与业务涉众沟通收集变更诉求；② 需求方直接提交正式 CR 变更需求文档。
- **阶段二 变更需求分析**：① A2 质量分析（合理性/完整性/无歧义）；② A3 更新 UML（用例图/活动图）；③ A4 输出变更版 SRS 初稿；④ A6 基线比对：读取历史基线，生成需求差异文档（新增/修改/删除/未变更），优化新版 SRS。
- **阶段三 变更审核（CCB）**：不通过→关闭；退回→回到阶段一；通过→进入新基线创立。
- **阶段四 新基线创立**：生成需求溯源矩阵建立变更前后映射；将通过的 SRS 定为新版正式基线；沿用版本规则编号；历史基线归档。

## 4.4 变更记录台账
| 变更编号 | 变更日期 | 申请人 | 变更来源(AI/CR) | 变更简述 | 影响模块 | CCB结论 | 新版基线号 |
|---|---|---|---|---|---|---|---|
| （初稿阶段尚无变更，进入基线后启用） | | | | | | | |"""

SEC5_APPENDIX = """# 5 附录

## 附录A 全量图表汇总
本 SRS 引用的 UML 模型源码与渲染图集中存放于 `wiki/summaries/uml/`（PlantUML）与 `wiki/summaries/uml/render/`（PNG），说明见 [[UML建模说明-v1.0]]：
- **系统总体用例图**：`uml/00_系统总体用例图.puml`
- **5 张子系统用例图**：`uml/uc_1_课程顾问.puml` … `uml/uc_5_系统管理员.puml`
- **6 张核心活动图**：`uml/act_01_报名优惠算价与审批.puml`、`act_02_试听锁定与候补`、`act_03_排课冲突检测`、`act_04_考勤与课时扣减`、`act_05_退费计算与审批`、`act_06_日终对账`
- **概念数据模型 E-R**、**系统架构图**、**变更流程图**：见正文 §2.1、§3.4、§4.2 的 Mermaid 代码块。

## 附录B 验收标准总表
> 完整验收要点见各 FR 的"验收标准"字段与 [[需求清单-v1.0]]；下表为 P0 关键需求摘录。

| 需求编号 | 需求名称 | 验收标准（量化） | 优先级 |
|---|---|---|---|
| FR-CRM-001 | 客户画像聚合 | 手机号查询后聚合页加载 ≤ 3s，含家庭/咨询/试听/报价/跟进/归属 | P0 |
| FR-TRIAL-002 | 试听名额锁定 | 并发独占，15 分钟倒计时自动释放，占用含前后各 5 分钟缓冲 | P0 |
| FR-ORDER-003 | 优惠分级审批 | ≤5000元且≥9折→主管30分钟超时自动通过；大额→校长4h/8h绝不自动通过 | P0 |
| FR-REF-001 | 退费计算 | 退费单价=实缴总额÷含赠送总课时，锁定不可改，发起即冻结参数快照 | P0 |
| FR-RECON-001 | 日终对账 | 日切18:00，四方(收款/报名/课消/余额)勾稽，异常强制推校长 | P0 |
| FR-ATT-002 | 考勤扣课时 | 状态机优先级固定，扣课时以是否到课为准，迟到≤15分钟不扣 | P0 |

## 附录C 参考资料与外部文档链接
1. GB/T 9385-2008 计算机软件需求规格说明规范
2. IEEE 830 软件需求规格说明书标准
3. 本项目：需求清单 v1.0、需求问题清单 v1.0/v2.0、CCB 裁决记录 v1.0、UML 建模说明 v1.0、5 类涉众首访/补访记录（`raw/notes/`）
4. 代码仓库：https://github.com/saucecat114514/Software-design-practice"""


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
