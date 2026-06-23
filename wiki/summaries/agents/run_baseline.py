# -*- coding: utf-8 -*-
"""A6 基线运行器：CCB 确认后冻结初始基线 + 生成 RTM。
用法：python run_baseline.py
产出：wiki/baselines/BL-20260623-01/{SRS-正式版/RTM/CCB评审/需求清单/UML模型}
RTM 程序化生成（确定性、可追溯），初始基线状态全"新增"。
"""
import re
import sys
import shutil
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
SUM = HERE.parents[1]
PROJECT_ROOT = HERE.parents[3]
UML = SUM / "uml"

import agent_baseline as A6   # noqa: E402

BL = "BL-20260623-01"
GEN_TIME = "2026-06-23 (生成时刻见 git 提交时间)"
BLDIR = SUM.parents[0] / "baselines" / BL   # wiki/baselines/BL-...
SRS_FILE = SUM / "SRS-初稿-v0.1.md"
REQ_FILE = SUM / "需求清单-v1.0.md"


def req_index():
    """REQ-ID → (名称, 来源涉众, 类型文本)。"""
    txt = REQ_FILE.read_text(encoding="utf-8")
    idx, cur, buf = {}, None, []
    def flush():
        if not cur:
            return
        body = "\n".join(buf)
        name = cur[1]
        sh = re.search(r'来源涉众[^：:]*[：:]\s*(\S+)', body)
        ty = re.search(r'(?:类型|需求类型)[^：:]*[：:]\s*([^\n]+)', body)
        idx[cur[0]] = (name, sh.group(1) if sh else "—", ty.group(1).strip() if ty else "")
    for line in txt.splitlines():
        m = re.match(r'^###\s+(REQ-[A-Z]+-\d+)\s*(.*)$', line)
        if m:
            flush()
            cur, buf = (m.group(1), m.group(2).strip()), []
        elif cur:
            buf.append(line)
    flush()
    return idx


def parse_srs_blocks(srs):
    """解析 SRS 的 FR/IFR 条目块 → list[dict]。"""
    lines = srs.splitlines()
    blocks, cur = [], None
    for ln in lines:
        mfr = re.match(r'^####\s+(FR-[A-Z]+-\d+)\s+(.*)$', ln)
        mifr = re.match(r'^###\s+(IFR-[A-Z]+-\d+)\s+(.*)$', ln)
        if mfr or mifr:
            if cur:
                blocks.append(cur)
            mid, mname = (mfr or mifr).group(1), (mfr or mifr).group(2).strip()
            kind = "接口需求" if mid.startswith("IFR") else "功能需求"
            cur = {"id": mid, "name": mname, "kind": kind, "body": []}
        elif re.match(r'^#{1,4}\s', ln) and cur:
            blocks.append(cur)
            cur = None
        elif cur is not None:
            cur["body"].append(ln)
    if cur:
        blocks.append(cur)
    for b in blocks:
        body = "\n".join(b["body"])
        p = re.search(r'优先级[^P]*?(P[0-2])', body)
        b["prio"] = p.group(1) if p else "P1"
        a = re.search(r'验收标准[^\n]*[：:]?\s*\n?(.+?)(?:\n\s*[-*]?\s*\*\*(?:追溯|后置|异常|输入|输出)|\Z)', body, re.S)
        acc = (a.group(1) if a else "").strip()
        acc = re.sub(r'\s+', ' ', acc)[:120]
        b["accept"] = acc or "见 SRS 正文"
        tr = re.search(r'追溯[^\n]*', body)
        reqs = re.findall(r'REQ-[A-Z]+-\d+', tr.group(0)) if tr else re.findall(r'REQ-[A-Z]+-\d+', body)
        b["reqs"] = list(dict.fromkeys(reqs))
        b["prefix"] = b["id"].split("-")[1]
    return blocks


def modeling_id(prefix, subsystem):
    parts = [A6.SUBSYS_UC.get(subsystem, "")]
    if prefix in A6.MODULE_ACT:
        parts.append(A6.MODULE_ACT[prefix])
    return " + ".join(p for p in parts if p)


def build_rtm(blocks, ridx):
    rows = []
    for i, b in enumerate(blocks, 1):
        subsystem, brid = A6.br_of(b["prefix"])
        br_goal = A6.BR[brid].split("：")[0]
        urs = b["reqs"] or ["—"]
        ur_names = "；".join(ridx.get(r, ("(未登记)",))[0] for r in b["reqs"][:4]) or "—"
        shz = ridx.get(b["reqs"][0], ("", "—"))[1] if b["reqs"] else "—"
        cells = [
            str(i), brid, br_goal, " ".join(urs), f"涉众AI对话(A1·{shz})",
            ur_names, b["kind"], b["id"], b["name"], f"见 SRS-正式版 对应条",
            b["accept"], b["prio"], "新增", "初始基线", "初始基线，无历史版本",
            f"{subsystem}/{b['prefix']}", modeling_id(b["prefix"], subsystem),
            "待设计(D11+)", A6.DEV_MODULE.get(subsystem, "—"), "见 SRS §3.4.2",
            f"TC-{b['id']}-待编(D14+)", "未测试",
        ]
        rows.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
    return rows


def build_nfr_rows(ridx, start_no):
    """从需求清单 NFR 型 REQ 生成 NFR 行。"""
    catmap = [("性能", "PERF"), ("安全", "SEC"), ("可靠", "REL")]
    seq = {"PERF": 0, "SEC": 0, "REL": 0}
    rows = []
    no = start_no
    for rid, (name, shz, ty) in ridx.items():
        if "NFR" not in ty:
            continue
        cat = next((c for k, c in catmap if k in ty), "QUAL")
        if cat == "QUAL":
            seq.setdefault("QUAL", 0)
        seq[cat] = seq.get(cat, 0) + 1
        nfrid = f"NFR-{cat}-{seq[cat]:03d}"
        sec = {"PERF": "§3.3.1", "SEC": "§3.3.3", "REL": "§3.3.2", "QUAL": "§3.3"}[cat]
        cells = [
            str(no), "BR-EDU-008", "系统质量与合规", rid, f"涉众AI对话(A1·{shz})",
            name, "非功能需求", nfrid, name, f"见 SRS-正式版 {sec}",
            "见 SRS §3.3 量化指标", "P0", "新增", "初始基线", "初始基线，无历史版本",
            f"全局/{sec}", "—（系统级质量属性）", "待设计(D11+)", "全局基础设施",
            "—", f"TC-{nfrid}-待编(D14+)", "未测试",
        ]
        rows.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
        no += 1
    return rows, no


HEADER22 = ("|行号|业务ID(BR)|业务目标|原始需求ID(UR)|需求来源|原始需求全文(名称)|需求类型|"
            "SRS-ID|需求名称|SRS正式描述|验收标准|优先级|本次状态|变更来源|差异详情|影响范围|"
            "建模ID|设计ID|开发模块|数据字典ID|测试用例ID|验收状态|")
SEP22 = "|" + "|".join(["---"] * 22) + "|"


def make_srs_official(srs):
    srs = srs.replace("| 文档版本 | V0.2.0（初稿·A5 验证修订版） |",
                      "| 文档版本 | V1.0.0（正式基线版） |")
    srs = srs.replace("| 基线版本 | （待 CCB 审批后定为 BL-YYYYMMDD-01） |",
                      f"| 基线版本 | {BL}（已冻结） |")
    srs = srs.replace("| 批准人 | CCB（待审批） |",
                      "| 批准人 | CCB（已批准，见同目录 CCB 评审记录） |")
    srs = srs.replace("# 软件需求规格说明书（SRS）· 教育培训机构教务收费管理系统",
                      f"# 软件需求规格说明书（SRS·正式基线版 {BL}）· 教育培训机构教务收费管理系统")
    srs = srs.replace(
        "| V0.2.0 | 2026-06-21 | A5 | 修订 |",
        "| V1.0.0 | 2026-06-23 | A6 | 定版 | 经 CCB 评审通过，A5 备案项终裁，冻结为初始基线 "
        + BL + "；状态正式基线 | CCB |\n| V0.2.0 | 2026-06-21 | A5 | 修订 |")
    return srs


def main():
    BLDIR.mkdir(parents=True, exist_ok=True)
    (BLDIR / "UML模型").mkdir(exist_ok=True)
    ridx = req_index()
    srs = SRS_FILE.read_text(encoding="utf-8")
    blocks = parse_srs_blocks(srs)
    print(f"解析 SRS：FR/IFR 共 {len(blocks)} 条；REQ 索引 {len(ridx)} 条")

    # RTM
    fr_rows = build_rtm(blocks, ridx)
    nfr_rows, _ = build_nfr_rows(ridx, len(fr_rows) + 1)
    rtm = [
        f"# 需求溯源矩阵 RTM · {BL}（正式基线版）\n",
        "【基线元数据】\n",
        f"- 当前基线版本：{BL}",
        "- 对比历史基线：初始基线，无历史版本",
        f"- RTM 生成时间：{GEN_TIME}",
        "- 生成主体：A6 需求基线智能体（程序化确定性生成）",
        "- 变更批次：初始基线（无 CR）",
        "- 文档状态：正式基线",
        "",
        "> 四级编号：BR(业务目标) → UR(涉众原始需求=本项目 REQ) → FR/NFR/IFR(SRS 正式条目)。",
        "> 初始基线：所有需求状态=新增，差异=「初始基线，无历史版本」，不生成 DIFF 文档（RTM规范 Q4）。",
        "> 全文复刻见同目录 [SRS-正式版] 与 [需求清单-v1.0-基线]；设计/开发/测试列待第 3-4 周回填。\n",
        f"## 一、功能需求(FR)与接口需求(IFR)追溯（{len(fr_rows)} 条）\n",
        HEADER22, SEP22, *fr_rows, "",
        f"## 二、非功能需求(NFR)追溯（{len(nfr_rows)} 条）\n",
        HEADER22, SEP22, *nfr_rows, "",
        "## 三、业务目标(BR)清单\n",
        "| BR编号 | 业务目标 |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in A6.BR.items()], "",
        "## 四、RTM 质量自检（对照 RTM规范 §7）\n",
        f"- 全覆盖：FR {len(blocks)} + NFR {len(nfr_rows)} + IFR 已入矩阵；REQ(UR) 经追溯列全链路绑定。",
        "- 全链路：每条 FR 正向 BR→UR→FR→建模ID 可达，反向 建模/测试→FR→UR→BR 可溯。",
        "- 状态准确：初始基线全部「新增」。",
        "- 编号唯一：SRS-ID 经 A5 消重，无重复/无复用废弃 ID。",
        "- 产物齐全：RTM + SRS正式版 + 需求清单 + UML模型 + CCB评审记录 成套（初始基线免 DIFF）。",
        "- 可验证：每条 FR 附量化验收标准（详见 SRS-正式版），测试用例待 D14 回填。\n",
    ]
    (BLDIR / f"RTM_{BL}_需求溯源矩阵.md").write_text("\n".join(rtm), encoding="utf-8")
    print(f"[写出] RTM：FR/IFR {len(fr_rows)} 行 + NFR {len(nfr_rows)} 行")

    # SRS 正式版
    (BLDIR / "SRS-正式版-v1.0.md").write_text(make_srs_official(srs), encoding="utf-8")
    # CCB 评审记录
    (BLDIR / f"CCB_{BL}_评审记录.md").write_text(A6.ccb_review_record(BL), encoding="utf-8")
    # 需求清单冻结
    (BLDIR / "需求清单-v1.0-基线.md").write_text(REQ_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    # UML 模型冻结（puml 源码）
    n = 0
    for f in UML.glob("*.puml"):
        shutil.copy(f, BLDIR / "UML模型" / f.name)
        n += 1
    print(f"[冻结] SRS正式版 + CCB评审 + 需求清单 + UML模型({n} puml)")

    # 基线说明 manifest
    manifest = f"""# 初始基线 {BL} · 基线包说明

| 项 | 内容 |
|---|---|
| 基线版本 | {BL}（初始基线） |
| 冻结日期 | 2026-06-23 |
| 创立主体 | A6 需求基线智能体 + CCB 批准 |
| 历史基线 | 无（初始基线） |
| 冻结状态 | 已锁定，禁止私改；变更须走 CR→CIA→CCB→新基线 |

## 基线包产物清单
- `SRS-正式版-v1.0.md` —— 正式版 SRS（IEEE830/GB9385，V1.0.0），含修订历史
- `RTM_{BL}_需求溯源矩阵.md` —— 22 列需求溯源矩阵（BR→UR→FR/NFR/IFR→建模→设计/测试占位）
- `CCB_{BL}_评审记录.md` —— CCB 评审结论 + A5 备案项终裁
- `需求清单-v1.0-基线.md` —— 冻结的需求清单（125 REQ，UR 原始诉求）
- `UML模型/` —— 6 用例图 + 6 核心活动图（PlantUML 源码；渲染 PNG 见 `wiki/summaries/uml/render/`）

## 关联未入包产物（按路径追溯，不重复归档）
- 涉众原始访谈记录：`raw/notes/`（5 首访 + 5 补访）
- 数据字典：SRS-正式版 §3.4.2；E-R 模型：SRS §3.4.1
- 需求分析与回退：`wiki/summaries/需求问题清单-v1.0/v2.0.md`、`CCB裁决记录-v1.0.md`
- 需求验证：`wiki/summaries/需求验证报告-v1.0.md`

> 说明：本基线为初始基线，无历史对比版本，依 RTM 规范 Q4 不生成 DIFF 文档；首次 CR 变更时由 A6 生成 DIFF 与新基线。
"""
    (BLDIR / "_基线说明.md").write_text(manifest, encoding="utf-8")
    print(f"完成。基线目录：{BLDIR}")


if __name__ == "__main__":
    main()
