# -*- coding: utf-8 -*-
"""
D11 · 需求知识图谱构建器（正向图谱 / Forward Knowledge Graph）
=================================================================
职责：扫描已冻结的需求基线 RTM（BL-20260623-01），**确定性**抽取三类节点与边：
  - Component（组件/业务模块）：由 RTM 中 功能需求(FR) 按模块聚合而来
  - Interface（接口/外部边界）：由 RTM 中 接口需求(IFR) 而来
  - Constraint（约束/质量属性）：由 RTM 中 非功能需求(NFR) + CCB 关键量化裁决 而来
并产出：
  - knowledge-graph.json   机器可读图谱（节点 + 边 + 指标），供 D12 MDS/DTS、D15 RCR 逆向比对复用
  - 知识图谱-v1.0.md       人读版（统计 + 节点表 + Mermaid 子系统级可视化 + 五维度量化输入）

方法论：CodeGraph 正向建模思路——把"设计意图"结构化成图，作为 ADR-001 架构选型的量化底座。
设计原则：纯解析、无 LLM、可复现（对齐 A6 程序化确定性生成）。基线只读，绝不修改。

用法：python build_knowledge_graph.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # D:\Project
BASELINE = ROOT / "wiki" / "baselines" / "BL-20260623-01"
RTM_FILE = BASELINE / "RTM_BL-20260623-01_需求溯源矩阵.md"
OUTDIR = ROOT / "wiki" / "summaries" / "design"
JSON_OUT = OUTDIR / "knowledge-graph.json"
MD_OUT = OUTDIR / "知识图谱-v1.0.md"

SOURCE_BASELINE = "BL-20260623-01"
GRAPH_ID = "KG-EDU-V1"

# ===== 子系统 → Spring 开发服务（取自 RTM 开发模块列 / agent_baseline.DEV_MODULE）=====
DEV_SVC = {
    "招生与客户管理": "crm-service",
    "教务管理": "academic-service",
    "财务管理": "finance-service",
    "经营管理": "bi-service",
    "系统管理": "admin-service",
    "综合": "platform-common",
}

# ===== 模块缩写 → 简明中文标签（人读用；缺省回退到缩写本身）=====
MODULE_LABEL = {
    "CRM": "客户线索与画像", "TRIAL": "试听名额与候补", "ORDER": "报名订单与优惠",
    "SCH": "排课与冲突检测", "CLS": "班级容量与候补", "ATT": "考勤与课时扣减",
    "MAKEUP": "补课额度管理", "RSCH": "调课管理", "TRP": "教务报表",
    "TRF": "转班与费用", "TREF": "教务退费", "MCAM": "多校区数据",
    "FIN": "课消与课时费", "RECON": "支付对账", "PAY": "收款认领与拆分",
    "REF": "退费计算与审批", "REV": "收入确认", "FEE": "欠费续费催缴",
    "INV": "发票管理", "PAYROLL": "教师工资核算", "FRP": "经营利润报表",
    "AUD": "财务审计追溯", "DASH": "经营看板", "ENROLL": "招生渠道分析",
    "OPS": "教师效能与满班率", "FMN": "实时课消监控", "APPROVAL": "关键财务审批",
    "CAMPUS": "分级审批与数据权限", "MOBILE": "移动端集成", "MINI": "家长端与小程序",
    "ORG": "组织架构", "ACC": "权限模板与授权", "BIZ": "业务规则配置",
    "DR": "灾备与恢复", "AUDIT": "审计日志", "SEC": "安全策略与告警",
    "PAYIF": "支付接口兜底", "ALERT": "异常预警中心", "MSG": "统一通知",
}

# ===== 基础/通用模块种子（取自 00_项目总作战计划 §7 通用基础模块 + 业务基础模块）=====
# 这些是架构选型时必须显式纳入的横切关注点，标注来源以便审计；不是凭空捏造。
BASE_MODULES = [
    {"id": "BASE-GATEWAY", "name": "支付网关", "kind": "通用基础", "consumers": ["finance-service", "crm-service"]},
    {"id": "BASE-INTEGRATION", "name": "第三方对接(短信/电票/小程序)", "kind": "通用基础", "consumers": ["finance-service", "academic-service", "bi-service"]},
    {"id": "BASE-CACHE", "name": "缓存", "kind": "通用基础", "consumers": ["bi-service", "crm-service"]},
    {"id": "BASE-SCHED", "name": "定时任务(对账/催缴/灾备演练)", "kind": "通用基础", "consumers": ["finance-service", "admin-service"]},
    {"id": "BASE-NOTIFY", "name": "通知中心", "kind": "业务基础", "consumers": ["academic-service", "crm-service", "bi-service", "finance-service"]},
    {"id": "BASE-APPROVAL", "name": "审批流引擎", "kind": "业务基础", "consumers": ["finance-service", "crm-service", "academic-service", "bi-service"]},
    {"id": "BASE-RBAC", "name": "账号权限(RBAC×校区)", "kind": "业务基础", "consumers": ["admin-service"]},
    {"id": "BASE-AUDIT", "name": "日志审计", "kind": "业务基础", "consumers": ["admin-service", "finance-service"]},
    {"id": "BASE-ORG", "name": "校区组织隔离", "kind": "业务基础", "consumers": ["admin-service"]},
    {"id": "BASE-CONFIG", "name": "系统参数配置", "kind": "业务基础", "consumers": ["admin-service"]},
]

# ===== CCB 关键量化约束（取自 BL-20260623-01 CCB 评审记录 二节备案终裁）=====
# 这些阈值/公式直接影响架构（可配置化、参数快照、并发独占、RTO 等），故纳入图谱 Constraint 层。
CCB_CONSTRAINTS = [
    {"id": "CON-CCB-001", "name": "排课/试听占用缓冲", "value": "默认5分钟，可配[1~30]", "impact": "可配置化/规则引擎"},
    {"id": "CON-CCB-002", "name": "赠送课时退费折价系数", "value": "默认1.0，可配[0~1]", "impact": "参数快照冻结"},
    {"id": "CON-CCB-003", "name": "发票自动开票审核阈值", "value": "默认5000元，可配", "impact": "可配置化"},
    {"id": "CON-CCB-004", "name": "续费提醒参数", "value": "提前7天/间隔3天/最多3次", "impact": "定时任务+可配置"},
    {"id": "CON-CCB-005", "name": "班级请假率预警阈值", "value": "单周20%/单月30%", "impact": "实时监控+告警"},
    {"id": "CON-CCB-006", "name": "核心库灾备 RTO", "value": "30分钟切换/零丢失", "impact": "异地灾备/高可用"},
    {"id": "CON-CCB-007", "name": "退费分级审批", "value": "三级强制，大额绝不自动通过", "impact": "审批流+权限"},
    {"id": "CON-CCB-008", "name": "试听名额并发独占", "value": "锁定独占+15分钟倒计时释放", "impact": "并发控制/分布式锁"},
]

# ===== 系统级容量基线（取自 SRS §3.3 / 作战计划 §7 系统管理）=====
CAPACITY = {
    "用户规模": "约 500 用户",
    "并发": "约 100 并发",
    "关键响应": "报名/缴费/查名额 ≤3s（试听 P99≤3s，目标≤1s）",
    "可用性目标": "灾备 RTO 30min / RPO≈5min",
    "部署": "阿里云单体部署（实训本机等效）",
}

ROW_RE = re.compile(r"^\|\s*\d+\s*\|")


def parse_rtm():
    """解析 RTM 表格，返回所有数据行（list[dict]）。列序对齐 RTM 表头。"""
    rows = []
    for line in RTM_FILE.read_text(encoding="utf-8").splitlines():
        if not ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 20:
            continue
        rows.append({
            "no": cells[0],
            "br": cells[1],
            "br_goal": cells[2],
            "ur": cells[3],
            "kind": cells[6],           # 功能需求/接口需求/非功能需求
            "srs_id": cells[7],
            "srs_name": cells[8],
            "priority": cells[11],
            "scope": cells[15],         # 影响范围，如 "招生与客户管理/CRM" 或 "全局/§3.3.1"
            "model_id": cells[16],      # 建模ID
            "dev_module": cells[18],    # 开发模块
        })
    return rows


def split_scope(scope):
    """'招生与客户管理/CRM' -> ('招生与客户管理', 'CRM')"""
    if "/" in scope:
        sub, mod = scope.split("/", 1)
        return sub.strip(), mod.strip()
    return scope.strip(), ""


def ur_prefix(ur):
    """'REQ-CRM-001 REQ-CRM-002' -> 'CRM'（取首个 REQ 的模块段）"""
    m = re.search(r"REQ-([A-Z]+)-", ur)
    return m.group(1) if m else ""


def build():
    rows = parse_rtm()
    nodes, edges = [], []
    components = {}   # mod_code -> node dict
    interfaces = []
    constraints = []

    fr_rows = [r for r in rows if r["kind"] == "功能需求"]
    ifr_rows = [r for r in rows if r["kind"] == "接口需求"]
    nfr_rows = [r for r in rows if r["kind"] == "非功能需求"]

    # ---- Component 节点：FR 按模块聚合 ----
    for r in fr_rows:
        sub, mod = split_scope(r["scope"])
        if not mod:
            continue
        comp = components.get(mod)
        if comp is None:
            comp = {
                "id": f"COMP-{mod}",
                "type": "Component",
                "code": mod,
                "name": MODULE_LABEL.get(mod, mod),
                "subsystem": sub,
                "br": r["br"],
                "dev_service": DEV_SVC.get(sub, "platform-common"),
                "realizes": [],
                "models": set(),
                "provenance": "RTM/功能需求聚合",
            }
            components[mod] = comp
        comp["realizes"].append(r["srs_id"])
        # 建模 ID（用例图 + 活动图），拆出 uc_/act_ 锚点
        for tok in re.findall(r"(uc_\d+_[^\s+]+|act_\d+_[^\s+]+)", r["model_id"]):
            comp["models"].add(tok)
        edges.append({"from": comp["id"], "rel": "realizes", "to": r["srs_id"]})
        edges.append({"from": comp["id"], "rel": "traces_to", "to": r["br"]})

    # ---- Interface 节点：IFR ----
    for r in ifr_rows:
        sub, mod = split_scope(r["scope"])
        node = {
            "id": r["srs_id"],
            "type": "Interface",
            "name": r["srs_name"],
            "boundary": "外部第三方/系统集成",
            "subsystem": sub,
            "br": r["br"],
            "provenance": "RTM/接口需求",
        }
        interfaces.append(node)
        # 依赖该接口的组件：同模块码组件优先；通知类(MSG)归通知中心基础模块
        consumer = components.get(mod)
        if consumer:
            edges.append({"from": consumer["id"], "rel": "depends_on", "to": node["id"]})
        else:
            # 跨切关注（如 MSG 通知、综合域）挂到对应基础模块
            base = "BASE-NOTIFY" if mod in ("MSG",) else "BASE-INTEGRATION"
            edges.append({"from": base, "rel": "depends_on", "to": node["id"]})

    # ---- Constraint 节点：NFR ----
    cat_map = {"PERF": "性能", "SEC": "安全", "REL": "可靠性"}
    for r in nfr_rows:
        mid = r["srs_id"].split("-")
        cat = cat_map.get(mid[1], mid[1]) if len(mid) > 1 else "质量"
        node = {
            "id": r["srs_id"],
            "type": "Constraint",
            "name": r["srs_name"],
            "category": cat,
            "scope": "全局",
            "provenance": "RTM/非功能需求",
        }
        constraints.append(node)
        # 约束作用的组件：经 UR 前缀回链；命中则约束该组件，否则约束系统根
        pfx = ur_prefix(r["ur"])
        target = components.get(pfx)
        if target:
            edges.append({"from": target["id"], "rel": "constrained_by", "to": node["id"]})
        else:
            edges.append({"from": "SYS-EDU", "rel": "constrained_by", "to": node["id"]})

    # ---- CCB 关键量化约束（追加 Constraint 节点）----
    for c in CCB_CONSTRAINTS:
        constraints.append({
            "id": c["id"], "type": "Constraint", "name": c["name"],
            "category": "业务量化(CCB)", "value": c["value"],
            "arch_impact": c["impact"], "scope": "全局",
            "provenance": "CCB评审记录/二节备案终裁",
        })
        edges.append({"from": "SYS-EDU", "rel": "constrained_by", "to": c["id"]})

    # ---- 系统根节点 ----
    sys_node = {
        "id": "SYS-EDU", "type": "System",
        "name": "教育培训机构教务收费管理系统",
        "capacity": CAPACITY, "provenance": "SRS §3.3 / 作战计划 §7",
    }

    # ---- 基础模块节点 + 边 ----
    base_nodes = []
    for b in BASE_MODULES:
        base_nodes.append({
            "id": b["id"], "type": "BaseModule", "name": b["name"],
            "kind": b["kind"], "provenance": "作战计划 §7 通用/业务基础模块",
        })
        for svc in b["consumers"]:
            edges.append({"from": svc, "rel": "served_by_base", "to": b["id"]})

    # ---- 收尾：固化 component 集合（set 转 list）----
    comp_list = []
    for comp in components.values():
        comp["models"] = sorted(comp["models"])
        comp["fr_count"] = len(comp["realizes"])
        comp_list.append(comp)
    comp_list.sort(key=lambda c: (c["subsystem"], c["code"]))

    nodes = [sys_node] + comp_list + interfaces + constraints + base_nodes

    # ---- 指标（喂给五维度架构选型）----
    by_sub = {}
    for comp in comp_list:
        s = comp["subsystem"]
        by_sub.setdefault(s, {"components": 0, "fr": 0})
        by_sub[s]["components"] += 1
        by_sub[s]["fr"] += comp["fr_count"]

    metrics = {
        "fr_count": len(fr_rows),
        "ifr_count": len(ifr_rows),
        "nfr_count": len(nfr_rows),
        "component_count": len(comp_list),
        "subsystem_count": len(by_sub),
        "interface_count": len(interfaces),
        "constraint_count": len(constraints),
        "base_module_count": len(base_nodes),
        "node_total": len(nodes),
        "edge_total": len(edges),
        "by_subsystem": by_sub,
        "capacity": CAPACITY,
        "five_dimension_inputs": {
            "功能复杂度": f"{len(fr_rows)} FR + {len(ifr_rows)} IFR 跨 {len(comp_list)} 业务组件 / {len(by_sub)} 子系统，以 CRUD+审批+对账类事务为主，非算法密集",
            "并发性能": f"{CAPACITY['并发']}、{CAPACITY['用户规模']}；关键路径 {CAPACITY['关键响应']}；无超高并发/秒杀级诉求",
            "可扩展性": "多校区数据隔离+汇总、规则可配置化（CCB 8 项量化约束多为可配），水平扩展诉求中等",
            "团队规模": "1 人全量执行（AI 辅助），无多团队并行开发诉求",
            "运维能力": f"{CAPACITY['部署']}；{CAPACITY['可用性目标']}；无独立 SRE/复杂分布式运维条件",
        },
    }

    graph = {
        "meta": {
            "graph_id": GRAPH_ID,
            "title": "教育培训机构教务收费管理系统 · 需求正向知识图谱",
            "source_baseline": SOURCE_BASELINE,
            "generated_from": RTM_FILE.name,
            "generator": "build_knowledge_graph.py（确定性解析，无 LLM）",
            "node_total": len(nodes),
            "edge_total": len(edges),
        },
        "metrics": metrics,
        "nodes": nodes,
        "edges": edges,
    }
    return graph


def render_md(graph):
    m = graph["metrics"]
    L = []
    L.append("# 需求知识图谱 v1.0 · 正向图谱（设计意图）")
    L.append("")
    L.append("> 生成方式：`build_knowledge_graph.py` 确定性解析基线 RTM，无 LLM、可复现。")
    L.append(f"> 图谱编号：{graph['meta']['graph_id']}　来源基线：{graph['meta']['source_baseline']}　"
             f"源文件：{graph['meta']['generated_from']}")
    L.append("> 用途：① 作为 D11 ADR-001 架构选型的量化底座；② 作为 D12 MDS/DTS 模块划分种子；"
             "③ 作为 D15 CodeGraph 逆向比对的正向基准。")
    L.append("> 配套机器可读件：[knowledge-graph.json](knowledge-graph.json)。")
    L.append("")
    L.append("## 一、图谱规模总览")
    L.append("")
    L.append("| 指标 | 数值 |")
    L.append("|---|---|")
    L.append(f"| 功能需求 FR | {m['fr_count']} |")
    L.append(f"| 接口需求 IFR | {m['ifr_count']} |")
    L.append(f"| 非功能需求 NFR | {m['nfr_count']} |")
    L.append(f"| 业务组件 Component | {m['component_count']} |")
    L.append(f"| 子系统 Subsystem | {m['subsystem_count']} |")
    L.append(f"| 接口边界 Interface | {m['interface_count']} |")
    L.append(f"| 约束 Constraint（NFR+CCB量化） | {m['constraint_count']} |")
    L.append(f"| 基础模块 BaseModule | {m['base_module_count']} |")
    L.append(f"| 节点总数 | {m['node_total']} |")
    L.append(f"| 边总数 | {m['edge_total']} |")
    L.append("")

    L.append("## 二、子系统 × 组件 × FR 分布")
    L.append("")
    L.append("| 子系统 | 开发服务 | 组件数 | FR 数 |")
    L.append("|---|---|---|---|")
    for sub, d in sorted(m["by_subsystem"].items(), key=lambda x: -x[1]["fr"]):
        L.append(f"| {sub} | {DEV_SVC.get(sub, 'platform-common')} | {d['components']} | {d['fr']} |")
    L.append("")

    L.append("## 三、Component 节点清单（业务组件）")
    L.append("")
    L.append("| 组件ID | 名称 | 子系统 | 业务目标 | FR数 | 关联建模 |")
    L.append("|---|---|---|---|---|---|")
    for n in graph["nodes"]:
        if n["type"] != "Component":
            continue
        models = "、".join(n["models"]) if n["models"] else "—"
        L.append(f"| {n['id']} | {n['name']} | {n['subsystem']} | {n['br']} | {n['fr_count']} | {models} |")
    L.append("")

    L.append("## 四、Interface 节点清单（外部边界）")
    L.append("")
    L.append("| 接口ID | 名称 | 边界 | 所属子系统 |")
    L.append("|---|---|---|---|")
    for n in graph["nodes"]:
        if n["type"] != "Interface":
            continue
        L.append(f"| {n['id']} | {n['name']} | {n['boundary']} | {n['subsystem']} |")
    L.append("")

    L.append("## 五、Constraint 节点清单（质量属性 + CCB 量化约束）")
    L.append("")
    L.append("| 约束ID | 名称 | 类别 | 取值/影响 |")
    L.append("|---|---|---|---|")
    for n in graph["nodes"]:
        if n["type"] != "Constraint":
            continue
        extra = n.get("value", "") or n.get("arch_impact", "") or "见 SRS §3.3 量化指标"
        L.append(f"| {n['id']} | {n['name']} | {n['category']} | {extra} |")
    L.append("")

    L.append("## 六、基础/通用模块（横切关注点，架构选型必纳入）")
    L.append("")
    L.append("| 模块ID | 名称 | 类别 |")
    L.append("|---|---|---|")
    for n in graph["nodes"]:
        if n["type"] != "BaseModule":
            continue
        L.append(f"| {n['id']} | {n['name']} | {n['kind']} |")
    L.append("")

    L.append("## 七、子系统级架构拓扑（Mermaid 可视化）")
    L.append("")
    L.append("> 组件→FR 的细粒度边见 knowledge-graph.json；此处为子系统/接口/基础设施的可读拓扑。")
    L.append("")
    L.append("```mermaid")
    L.append("graph TD")
    L.append("  USER(\"5 类涉众 / 家长端\") --> GW(\"统一接入层\")")
    L.append("  GW --> CRM(\"crm-service 招生客户\")")
    L.append("  GW --> ACA(\"academic-service 教务\")")
    L.append("  GW --> FIN(\"finance-service 财务\")")
    L.append("  GW --> BI(\"bi-service 经营BI\")")
    L.append("  GW --> ADM(\"admin-service 系统管理\")")
    L.append("  CRM --> COMMON(\"platform-common 基础设施\")")
    L.append("  ACA --> COMMON")
    L.append("  FIN --> COMMON")
    L.append("  BI --> COMMON")
    L.append("  ADM --> COMMON")
    L.append("  COMMON --> PAYIF(\"IFR 支付渠道兜底\")")
    L.append("  COMMON --> INVIF(\"IFR 电子发票\")")
    L.append("  COMMON --> MSGIF(\"IFR 统一通知\")")
    L.append("  COMMON --> MINIIF(\"IFR 家长小程序同步\")")
    L.append("  COMMON --> FINIF(\"IFR 第三方财务对接\")")
    L.append("  COMMON --> DB(\"关系型数据库 + 缓存\")")
    L.append("```")
    L.append("")

    L.append("## 八、五维度架构选型量化输入（供 ADR-001 / ASD）")
    L.append("")
    L.append("> 下列五维直接喂入 D11 ADR-001 的架构选型评估，结论锚点全部来自本图谱与基线，不拍脑袋。")
    L.append("")
    L.append("| 维度 | 量化画像（来自图谱/基线） |")
    L.append("|---|---|")
    for k, v in m["five_dimension_inputs"].items():
        L.append(f"| {k} | {v} |")
    L.append("")
    L.append("**系统容量基线**：" + "；".join(f"{k} {v}" for k, v in m["capacity"].items()) + "。")
    L.append("")
    L.append("> 结论预判（详见 ADR-001）：功能复杂度中等且以事务型 CRUD+审批+对账为主、"
             "并发与运维诉求中等、单人开发——**四层分层架构（Controller→Service→Repository→Model）** "
             "在 AI 代码生成适配性、落地成本、可校验性上最优；DDD（过度设计）与轻量微服务（运维成本不匹配）淘汰。")
    L.append("")
    return "\n".join(L)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    graph = build()
    JSON_OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    MD_OUT.write_text(render_md(graph), encoding="utf-8")
    m = graph["metrics"]
    print(f"[OK] 知识图谱已生成")
    print(f"  - {JSON_OUT}")
    print(f"  - {MD_OUT}")
    print(f"  节点 {m['node_total']}（Component {m['component_count']} / Interface {m['interface_count']} "
          f"/ Constraint {m['constraint_count']} / BaseModule {m['base_module_count']}），边 {m['edge_total']}")
    print(f"  FR {m['fr_count']} / IFR {m['ifr_count']} / NFR {m['nfr_count']}，子系统 {m['subsystem_count']}")


if __name__ == "__main__":
    main()
