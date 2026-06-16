# -*- coding: utf-8 -*-
"""A2 需求分析运行器：合并 5 份需求记录 → 四维质量检测 → 输出问题清单。
用法：python run_analysis.py
输出：wiki/summaries/需求清单-v1.0.md、wiki/summaries/需求问题清单-v1.0.md
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
PROJECT_ROOT = HERE.parents[3]
RAW = PROJECT_ROOT / "raw" / "notes"
SUM = HERE.parents[1]            # wiki/summaries

import llm_config as L           # noqa: E402
import agent_analyst as A2       # noqa: E402

# 固定涉众顺序
ORDER = ["课程顾问", "教务老师", "财务人员", "校长", "系统管理员"]


def find_files():
    files = {}
    for f in RAW.glob("*.md"):
        if f.name.startswith("_"):
            continue
        role = f.name.split("-")[0]
        files[role] = f
    return [(r, files[r]) for r in ORDER if r in files]


def main():
    pairs = find_files()
    print("找到需求记录:", [r for r, _ in pairs])

    # ===== Step A：逐角色合并为干净需求清单 =====
    consolidated = []
    for role, f in pairs:
        raw = f.read_text(encoding="utf-8")
        print(f"[合并] {role} 原文 {len(raw)} 字 …")
        out = L.chat_complete(
            [{"role": "system", "content": A2.consolidate_prompt(role)},
             {"role": "user", "content": raw}],
            max_tokens=4096, max_rounds=8,
        )
        n = len(set(re.findall(r'REQ-[A-Z]+-\d+', out)))
        print(f"        → 清单 {len(out)} 字，唯一 REQ {n} 条")
        consolidated.append((role, out))

    combined = "\n\n".join(c for _, c in consolidated)
    reqlist_md = (
        "# 需求清单（A2 合并版）· v1.0\n\n"
        "> 由 A2 需求分析智能体从 5 份 raw/notes 访谈记录去重合并而成。"
        "下游：A2 质量分析、A3 建模、A4 SRS。见 [[00_项目总作战计划]]。\n\n---\n\n"
        + combined + "\n"
    )
    (SUM / "需求清单-v1.0.md").write_text(reqlist_md, encoding="utf-8")
    total_req = len(set(re.findall(r'REQ-[A-Z]+-\d+', combined)))
    print(f"[写出] 需求清单-v1.0.md，合计唯一 REQ {total_req} 条")

    # ===== Step B：四维质量分析 =====
    print("[分析] 四维质量检测中 …")
    problems = L.chat_complete(
        [{"role": "system", "content": A2.analysis_prompt()},
         {"role": "user", "content": combined}],
        max_tokens=4096, max_rounds=10,
    )
    prob_md = (
        "# 需求问题清单（A2 四维质量分析）· v1.0\n\n"
        "> A2 对全量需求清单做 模糊/不一致/矛盾/冲突 检测的产出；含回退记录。"
        "冲突仅报告、由 CCB 裁决。见 [[需求清单-v1.0]]、[[00_项目总作战计划]]。\n\n---\n\n"
        + problems + "\n"
    )
    (SUM / "需求问题清单-v1.0.md").write_text(prob_md, encoding="utf-8")
    n_issue = len(re.findall(r'ISSUE-\d+', problems))
    print(f"[写出] 需求问题清单-v1.0.md，检出问题(ISSUE)约 {n_issue} 条")
    print("完成。")


if __name__ == "__main__":
    main()
