# -*- coding: utf-8 -*-
"""补访整合运行器：把 5 份补访记录的澄清结果对回 A2 问题清单，产出需求问题清单 v2.0。
用法：python run_followup_integration.py
输出：wiki/summaries/需求问题清单-v2.0.md
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
PROJECT_ROOT = HERE.parents[3]
RAW = PROJECT_ROOT / "raw" / "notes"
SUM = HERE.parents[1]

import llm_config as L           # noqa: E402
import agent_analyst as A2       # noqa: E402

ORDER = ["课程顾问", "教务老师", "财务人员", "校长", "系统管理员"]


def find_followups():
    files = {}
    for f in RAW.glob("*-补访记录.md"):
        role = f.name.split("-")[0]
        files[role] = f
    return [(r, files[r]) for r in ORDER if r in files]


def main():
    problems = (SUM / "需求问题清单-v1.0.md").read_text(encoding="utf-8")
    pairs = find_followups()
    print("找到补访记录:", [r for r, _ in pairs])

    sections = []
    for role, f in pairs:
        fu = f.read_text(encoding="utf-8")
        print(f"[整合] {role} 补访 {len(fu)} 字 …")
        out = L.chat_complete(
            [{"role": "system", "content": A2.integrate_prompt(role)},
             {"role": "user", "content": "## 原《需求问题清单》\n\n" + problems
              + "\n\n## 【" + role + "】补访记录\n\n" + fu}],
            max_tokens=4096, max_rounds=8,
        )
        sections.append(out.strip())
        print(f"        → 澄清 {len(out)} 字")

    body = (
        "# 需求问题清单 · v2.0（补访整合后）\n\n"
        "> 在 [[需求问题清单-v1.0]] 基础上，整合 5 类涉众补访的澄清结果。\n"
        "> 状态口径：`已澄清`=可据此修订需求；`部分澄清`=仍有残留；`待CCB裁决`=跨涉众冲突，需评审拍板。\n"
        "> 见 [[需求清单-v1.0]]、[[补访问题清单-v1.0]]、[[00_项目总作战计划]]。\n\n---\n\n"
        "## 一、补访澄清结果（按涉众）\n\n"
        + "\n\n".join(sections)
        + "\n\n---\n\n## 二、仍需 CCB 裁决的跨涉众冲突\n\n"
        "以下为本质属涉众间互斥诉求、补访只能各表立场的冲突，**最终由 CCB 裁决**（各方立场见上节及 v1.0 建议方向）：\n"
        "- **ISSUE-007** 退费基础单价口径：财务「总课时均价」 ↔ 教务「正课原价/赠课不折现」。\n"
        "- **ISSUE-008** 特殊审批时效 ↔ 校长风控刚性（分级+代理人+超时）。\n"
        "- **ISSUE-015** 赠课「只计成本不计收入」导致收入成本不配比（财务口径/科目归属）。\n"
        "- **ISSUE-023** 缴费渠道统一 ↔ 线下收款拆分（边界：仅财务操作+系统留痕）。\n"
    )
    (SUM / "需求问题清单-v2.0.md").write_text(body, encoding="utf-8")
    print(f"[写出] 需求问题清单-v2.0.md，共 {len(body)} 字")
    print("完成。")


if __name__ == "__main__":
    main()
