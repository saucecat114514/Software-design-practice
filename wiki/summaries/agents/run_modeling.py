# -*- coding: utf-8 -*-
"""A3 建模运行器：需求清单 + CCB 裁决 → 6 张用例图 + 6 张核心活动图（PlantUML）。
用法：python run_modeling.py [usecase|activity|overview|all]
输出：wiki/summaries/uml/*.puml
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
PROJECT_ROOT = HERE.parents[3]
SUM = HERE.parents[1]                 # wiki/summaries
UML = SUM / "uml"
UML.mkdir(exist_ok=True)

import llm_config as L                # noqa: E402
import agent_modeler as A3            # noqa: E402

REQ_FILE = SUM / "需求清单-v1.0.md"
CCB_FILE = SUM / "CCB裁决记录-v1.0.md"

# 五个子系统：名称 -> (需求清单中的 ## 章节名, 参与者提示)
SUBSYS = [
    ("招生与客户管理子系统", "课程顾问",
     "课程顾问(主)、家长/潜在客户(咨询·转介绍人)、校区主管/审批人(优惠特批)、支付渠道(统一收款)"),
    ("教务管理子系统", "教务老师",
     "教务老师(主)、授课教师、家长(填报不可用时段·请假·选补课·确认转班费用)、校区主管/校长(退款·跨日考勤审批)、第三方财务系统(课时费/退费对接)"),
    ("财务管理子系统", "财务人员",
     "财务人员(主)、支付渠道(对账单)、第三方电子发票平台、教务/销售(收款认领)、家长(回填付款·欠费催缴)、审批人(退费/拆分)、校长(对账异常报警接收)"),
    ("经营管理子系统", "校长",
     "校长/集团负责人(主)、校区主管(分级审批·数据范围)、课程顾问/授课教师(被考核对象)、家长(小程序:成长档案·自助请假调课·选课缴费)、第三方财务系统(渠道费用对接)"),
    ("系统管理子系统", "系统管理员",
     "系统管理员/超级管理员(主)、校长(政策配置审阅)、支付接口/支付渠道(异常兜底·单边账)、各业务角色(被授权对象)"),
]

ALL_ACTORS = ("课程顾问、教务老师、授课教师、财务人员、校区主管、校长/集团负责人、系统管理员、家长（学生家长端/小程序）；"
              "外部系统：支付渠道、第三方电子发票平台、第三方财务系统")
SUBSYS_LINE = "招生与客户管理、教务管理、财务管理、经营管理、系统管理"

# 六张核心活动图：(文件名key, 用例标题, 取用的需求章节)
ACTIVITIES = [
    ("01_报名优惠算价与审批", "报名优惠算价与分级审批路由", ["课程顾问", "校长"]),
    ("02_试听锁定与候补", "试听名额一键锁定与候补补位", ["课程顾问", "教务老师"]),
    ("03_排课冲突检测", "排课三维冲突检测与强制覆盖留痕", ["教务老师"]),
    ("04_考勤与课时扣减", "考勤签到与课时扣减/收入确认", ["教务老师", "财务人员"]),
    ("05_退费计算与审批", "退费金额计算与审批执行", ["财务人员", "教务老师"]),
    ("06_日终对账", "日终自动对账与资金四方勾稽", ["财务人员", "校长", "系统管理员"]),
]


def parse_sections(text):
    """按 '## 章节名' 切分需求清单为 {章节名: 正文}。"""
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


def fix_inline_comments(puml):
    """PlantUML 的 ' 注释只能在行首，不支持行尾内联。
    把形如 `usecase ... as X  ' REQ-001` 的行尾注释挪到上一行（行首注释，合法），保留 REQ 追溯。"""
    out = []
    for line in puml.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("'") or stripped.startswith("@") or "'" not in line:
            out.append(line)
            continue
        idx = line.find(" '")
        if idx == -1:
            out.append(line)
            continue
        indent = line[:len(line) - len(stripped)]
        code, comment = line[:idx].rstrip(), line[idx + 1:]
        out.append(indent + comment)   # 注释独占一行，置于代码行之上
        out.append(code)
    return "\n".join(out)


def extract_puml(s):
    """从模型回复中抽出 @startuml..@enduml 块。
    截断续写时模型常把整图重画一遍 → 取「最后一个 @startuml → 其后第一个 @enduml」，
    既能拿到重画后的完整图，也兼容正常的单图输出。"""
    starts = [m.start() for m in re.finditer(r'@startuml', s)]
    ends = [m.end() for m in re.finditer(r'@enduml', s)]
    if starts and ends:
        last_start = starts[-1]
        end_after = next((e for e in ends if e > last_start), ends[-1])
        if end_after > last_start:
            return fix_inline_comments(s[last_start:end_after].strip()) + "\n"
    return fix_inline_comments(s.strip()) + "\n"


def gen(system_prompt, user_content, fname, max_tokens=4096):
    out = L.chat_complete(
        [{"role": "system", "content": system_prompt},
         {"role": "user", "content": user_content}],
        temperature=0.4, max_tokens=max_tokens, max_rounds=8,
    )
    puml = extract_puml(out)
    (UML / fname).write_text(puml, encoding="utf-8")
    ok = puml.startswith("@startuml") and puml.rstrip().endswith("@enduml")
    print(f"  [写出] {fname}  ({len(puml)} 字, {'OK' if ok else '⚠ 结构待查'})")
    return puml


def main(mode="all"):
    if mode == "fix":
        for f in sorted(UML.glob("*.puml")):
            txt = f.read_text(encoding="utf-8")
            fixed = fix_inline_comments(txt.strip()) + "\n"
            f.write_text(fixed, encoding="utf-8")
            print(f"  [修复] {f.name}")
        print("完成。")
        return

    secs = parse_sections(REQ_FILE.read_text(encoding="utf-8"))
    print("解析到需求章节:", list(secs.keys()))
    ccb = CCB_FILE.read_text(encoding="utf-8")

    if mode in ("all", "overview"):
        print("[总体用例图]")
        # 总图只喂各子系统的用例标题级信息（REQ 名称行），保持粗粒度
        titles = []
        for name, sec, _ in SUBSYS:
            lines = [l for l in secs.get(sec, "").splitlines() if l.startswith("### REQ-")]
            titles.append(f"【{name}】\n" + "\n".join(lines))
        gen(A3.overview_prompt(ALL_ACTORS, SUBSYS_LINE),
            "\n\n".join(titles), "00_系统总体用例图.puml", max_tokens=4096)

    if mode in ("all", "usecase"):
        # 可选：python run_modeling.py usecase 2 3 仅重生成第 2、3 个子系统
        only = {int(a) for a in sys.argv[2:] if a.isdigit()} if mode == "usecase" else set()
        for i, (name, sec, hint) in enumerate(SUBSYS, 1):
            if only and i not in only:
                continue
            print(f"[用例图] {name}")
            gen(A3.usecase_prompt(name, hint), secs.get(sec, ""),
                f"uc_{i}_{sec}.puml", max_tokens=8000)

    if mode in ("all", "activity"):
        # 可选：python run_modeling.py activity 04 仅重生成 key 含 "04" 的活动图
        picks = list(sys.argv[2:]) if mode == "activity" else []
        for key, title, sources in ACTIVITIES:
            if picks and not any(p in key for p in picks):
                continue
            print(f"[活动图] {title}")
            req_text = "\n\n".join(f"# 需求章节：{s}\n{secs.get(s, '')}" for s in sources)
            user = (f"## 核心用例：{title}\n\n"
                    f"=== 一、相关需求条目 ===\n{req_text}\n\n"
                    f"=== 二、CCB 裁决记录（必须遵守其口径/阈值） ===\n{ccb}")
            gen(A3.activity_prompt(title), user, f"act_{key}.puml", max_tokens=8000)

    print("完成。输出目录:", UML)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
