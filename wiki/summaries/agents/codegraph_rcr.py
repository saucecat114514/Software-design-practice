# -*- coding: utf-8 -*-
"""
D15 · CodeGraph 逆向校验器（Reverse Check / RCR 引擎）
=================================================================
职责：静态解析 v1 代码（code/edu-charge-system），构建**实际逆向图谱**（类→分层/模块/依赖），
      与正向基线（module-catalog.json / dependency-topology.json / OAS / TLCD）做**六维比对**：
      架构 / 模块 / 拓扑 / 契约 / 代码 / 溯源，输出违规清单 ERR-NNNN（Blocker/Major/Minor）。
原则：以归档基线为唯一真值，不以代码现状为准（RCR 规范 §1.5.3）。纯解析无 LLM、可复现。
本机等效：以正则静态分析替代 tree-sitter（作战计划 §8 工具映射）。
用法：python codegraph_rcr.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODE = ROOT / "code" / "edu-charge-system" / "src" / "main" / "java"
DESIGN = ROOT / "wiki" / "summaries" / "design"
CATALOG = DESIGN / "module-catalog.json"
TOPO = DESIGN / "dependency-topology.json"
OAS = DESIGN / "oas" / "OAS_V2_教育培训收费系统_接口契约.yaml"
OUT = DESIGN / "report" / "rcr-findings.json"

# 包(域.模块slug) → MOD-ID（对齐 MDS / build_oas_inventory.SLUG）
PKG2MOD = {
    ("crm", "customer"): "MOD-001", ("crm", "trial"): "MOD-002", ("crm", "order"): "MOD-003",
    ("academic", "schedule"): "MOD-004", ("academic", "clazz"): "MOD-005",
    ("academic", "attendance"): "MOD-006", ("academic", "transfer"): "MOD-007",
    ("academic", "consume"): "MOD-008",
    ("finance", "payment"): "MOD-009", ("finance", "refund"): "MOD-010",
    ("finance", "invoice"): "MOD-011", ("finance", "revenue"): "MOD-012",
}
DOMAINS = {"crm", "academic", "finance", "bi", "admin"}
LAYERS = ("controller", "service", "repository", "model", "event", "listener", "config")


def parse_classes():
    """解析每个 .java：package / 类名 / 分层 / 模块 / com.edu 导入。"""
    classes = []
    for f in CODE.rglob("*.java"):
        text = f.read_text(encoding="utf-8")
        pkg_m = re.search(r"package\s+([\w.]+);", text)
        pkg = pkg_m.group(1) if pkg_m else ""
        cls_m = re.search(r"(?:public\s+)?(?:class|interface|enum|record)\s+(\w+)", text)
        cls = cls_m.group(1) if cls_m else f.stem
        imports = re.findall(r"import\s+(com\.edu\.[\w.]+);", text)
        parts = pkg.split(".")
        # 分层
        layer = next((seg for seg in parts if seg in LAYERS), "other")
        if len(parts) >= 3 and parts[2] == "common":
            layer = "base"
        # 模块
        mod = "app"
        if len(parts) >= 4 and parts[2] in DOMAINS:
            mod = PKG2MOD.get((parts[2], parts[3]), f"{parts[2]}.{parts[3]}")
        elif len(parts) >= 3 and parts[2] == "common":
            mod = "BASE-" + (parts[3] if len(parts) >= 4 else "common")
        classes.append({
            "file": str(f.relative_to(ROOT)).replace("\\", "/"),
            "pkg": pkg, "cls": cls, "layer": layer, "module": mod,
            "imports": imports, "text": text,
        })
    return classes


def layer_of_import(imp):
    for seg in imp.split("."):
        if seg in LAYERS:
            return seg
    if ".common." in imp:
        return "base"
    return "other"


def module_of_import(imp):
    parts = imp.split(".")
    if len(parts) >= 4 and parts[2] in DOMAINS:
        return PKG2MOD.get((parts[2], parts[3]), f"{parts[2]}.{parts[3]}")
    if len(parts) >= 4 and parts[2] == "common":
        return "BASE-" + parts[3]
    return "app"


def run_checks(classes):
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    topo = json.loads(TOPO.read_text(encoding="utf-8"))
    oas = OAS.read_text(encoding="utf-8")
    oas_paths = set(re.findall(r"^\s+(/api/[\w/{}-]+):", oas, re.M))
    whitelist = {(e["from"], e["to"]) for e in topo["edges"]}
    global_base = set(topo["meta"]["global_base"])

    findings = []
    eid = [0]

    def add(level, dim, basis, loc, desc, fix):
        eid[0] += 1
        findings.append({"err": f"ERR-{eid[0]:04d}", "level": level, "dim": dim,
                         "basis": basis, "loc": loc, "desc": desc, "fix": fix})

    # 维度命中统计
    dims = {d: {"checked": 0, "viol": 0} for d in
            ["架构", "模块", "拓扑", "契约", "代码", "溯源"]}

    # ---------- 2.1 架构维 ----------
    for c in classes:
        if c["layer"] == "controller":
            dims["架构"]["checked"] += 1
            for imp in c["imports"]:
                if layer_of_import(imp) == "repository":
                    dims["架构"]["viol"] += 1
                    add("Blocker", "架构", "C-ARCH-0002/ASD§2.2", c["file"],
                        f"Controller {c['cls']} 直接依赖 Repository（跨层穿透）", "改为经 Service 调用")
        if c["layer"] in ("repository", "model"):
            for imp in c["imports"]:
                if layer_of_import(imp) in ("controller", "service"):
                    dims["架构"]["viol"] += 1
                    add("Blocker", "架构", "C-ARCH-0002", c["file"],
                        f"{c['layer']} 层 {c['cls']} 反向依赖上层 {layer_of_import(imp)}", "移除反向依赖")
    # @Transactional 仅 Service
    for c in classes:
        if "@Transactional" in c["text"] and c["layer"] not in ("service",):
            dims["架构"]["viol"] += 1
            add("Major", "架构", "C-ARCH-0012/C-CODE-0011", c["file"],
                f"{c['cls']} 非 Service 层却含 @Transactional", "事务注解仅限 Service")

    # ---------- 2.2 模块维 ----------
    for c in classes:
        if c["module"].startswith("MOD-"):
            dims["模块"]["checked"] += 1
        for imp in c["imports"]:
            tgt_mod = module_of_import(imp)
            if tgt_mod.startswith("MOD-") and tgt_mod != c["module"] and c["module"].startswith("MOD-"):
                limp = layer_of_import(imp)
                # 跨模块只允许 service(调用) / event(订阅) / model.dto|vo(契约载体)；禁 repository / model.entity
                if limp == "repository" or ".model.entity." in imp:
                    dims["模块"]["viol"] += 1
                    add("Blocker", "模块", "C-MOD-0003/0004", c["file"],
                        f"{c['cls']} 跨模块直访 {tgt_mod} 的私有数据（{imp}）", "改为经对方 Service 接口")

    # ---------- 2.3 拓扑维 ----------
    actual_edges = set()
    for c in classes:
        if not c["module"].startswith("MOD-"):
            continue
        for imp in c["imports"]:
            tgt = module_of_import(imp)
            if tgt == c["module"]:
                continue
            limp = layer_of_import(imp)
            if tgt.startswith("MOD-"):
                # 事件订阅（消费者 import 生产者 .event）属合规解耦，不计入硬依赖边
                if limp == "event":
                    continue
                actual_edges.add((c["module"], tgt))
            elif tgt.startswith("BASE-"):
                actual_edges.add((c["module"], tgt))
    for (frm, tgt) in sorted(actual_edges):
        dims["拓扑"]["checked"] += 1
        # 基础模块映射到全局基础或具体 MOD-10x；这里业务→基础统一放行（白名单/全局基础矩阵）
        if tgt.startswith("BASE-"):
            continue
        if (frm, tgt) not in whitelist:
            dims["拓扑"]["viol"] += 1
            add("Blocker", "拓扑", "DTS 白名单", f"{frm}->{tgt}",
                f"跨模块依赖 {frm}->{tgt} 不在 DTS 白名单", "补白名单或移除依赖")
    # 反向：基础模块依赖业务
    for c in classes:
        if c["layer"] == "base":
            for imp in c["imports"]:
                if module_of_import(imp).startswith("MOD-"):
                    dims["拓扑"]["viol"] += 1
                    add("Blocker", "拓扑", "DTS §2/C-MOD-0007", c["file"],
                        f"基础模块 {c['cls']} 反向依赖业务模块", "基础模块禁依赖业务")
    # 环检测
    adj = {}
    for (a, b) in actual_edges:
        if a.startswith("MOD-") and b.startswith("MOD-"):
            adj.setdefault(a, []).append(b)
    if detect_cycle(adj):
        dims["拓扑"]["viol"] += 1
        add("Blocker", "拓扑", "DTS 无环原则", "业务模块", "存在循环依赖", "打破依赖环")

    # ---------- 2.4 契约维 ----------
    code_paths = set()
    for c in classes:
        if c["layer"] != "controller":
            continue
        base = re.search(r'@RequestMapping\("([^"]+)"\)', c["text"])
        base_path = base.group(1) if base else ""
        # 仅方法级映射（排除类级 @RequestMapping，避免基路径重复拼接）
        for sub in re.findall(r'@(?:Post|Get|Put|Patch|Delete)Mapping\("([^"]*)"\)', c["text"]):
            full = (base_path + sub) if sub else base_path
            code_paths.add(full)
    for p in sorted(code_paths):
        dims["契约"]["checked"] += 1
        if p not in oas_paths:
            dims["契约"]["viol"] += 1
            add("Blocker", "契约", "OAS 全覆盖", p,
                f"HTTP 接口 {p} 无 OAS 契约（私自新增）", "补 OAS 契约或删除")
    # 统一响应体
    for c in classes:
        if c["layer"] == "controller":
            for ret in re.findall(r"public\s+([\w<>]+)\s+\w+\(", c["text"]):
                if ret != "ApiResponse" and not ret.startswith("ApiResponse"):
                    dims["契约"]["viol"] += 1
                    add("Major", "契约", "C-CODE-0013", c["file"],
                        f"{c['cls']} 返回 {ret} 非统一 ApiResponse", "统一响应体")

    # ---------- 2.5 代码维 ----------
    for c in classes:
        dims["代码"]["checked"] += 1
        # 命名规范
        if c["layer"] == "controller" and not c["cls"].endswith("Controller"):
            dims["代码"]["viol"] += 1
            add("Minor", "代码", "C-CODE-0003", c["file"], f"{c['cls']} 命名不符 Controller 规范", "重命名")
        # Service 裸 SQL
        if c["layer"] == "service" and re.search(r"\b(select|insert|update|delete)\s+.*\bfrom\b", c["text"], re.I):
            dims["代码"]["viol"] += 1
            add("Blocker", "代码", "C-ARCH-0004/C-CODE-0007", c["file"],
                f"{c['cls']} 出现裸 SQL", "数据访问下沉 Repository")
        # 业务阈值硬编码（service impl 中 static final 数值常量）
        if c["layer"] == "service" and c["cls"].endswith("Impl"):
            for m in re.finditer(r"static\s+final[^\n=]*=\s*(?:new\s+BigDecimal\(\"[\d.]+\"\)|[\d.]+)", c["text"]):
                dims["代码"]["viol"] += 1
                add("Minor", "代码", "C-ARCH-0008/C-CODE-0012", c["file"],
                    f"{c['cls']} 存在硬编码业务阈值常量：{m.group(0).strip()[:60]}",
                    "迁移至配置注入（属业务规则配置 MOD-020）")

    # ---------- 2.6 溯源维 ----------
    impl_mods = {c["module"] for c in classes if c["module"].startswith("MOD-")}
    for c in classes:
        if c["layer"] == "controller":
            dims["溯源"]["checked"] += 1
            if not re.search(r"API-\d{4}|FR-[A-Z]+-\d{3}", c["text"]):
                dims["溯源"]["viol"] += 1
                add("Minor", "溯源", "RTM/OAS", c["file"],
                    f"{c['cls']} 缺少 API/FR 溯源注释", "补 x-api/FR 注释")

    return findings, dims, sorted(impl_mods), sorted(code_paths)


def detect_cycle(adj):
    color = {}

    def dfs(u):
        color[u] = 1
        for v in adj.get(u, []):
            if color.get(v, 0) == 1:
                return True
            if color.get(v, 0) == 0 and dfs(v):
                return True
        color[u] = 2
        return False

    return any(color.get(n, 0) == 0 and dfs(n) for n in list(adj))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    classes = parse_classes()
    findings, dims, impl_mods, paths = run_checks(classes)
    by_level = {"Blocker": 0, "Major": 0, "Minor": 0}
    for f in findings:
        by_level[f["level"]] += 1
    result = {
        "meta": {"engine": "codegraph_rcr.py", "classes": len(classes),
                 "impl_modules": impl_mods, "endpoints": paths},
        "summary": {"total": len(findings), **by_level,
                    "drift_excl_minor": by_level["Blocker"] + by_level["Major"]},
        "dimensions": dims,
        "findings": findings,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 逆向校验完成 → {OUT}")
    print(f"  类 {len(classes)}，实现模块 {impl_mods}，端点 {len(paths)}")
    print(f"  违规 总 {len(findings)}：Blocker {by_level['Blocker']} / Major {by_level['Major']} / Minor {by_level['Minor']}")
    print(f"  关键漂移(Blocker+Major) = {by_level['Blocker'] + by_level['Major']}（目标 ≤2、Blocker=0）")
    for f in findings:
        print(f"   - {f['err']} [{f['level']}/{f['dim']}] {f['desc']}")


if __name__ == "__main__":
    main()
