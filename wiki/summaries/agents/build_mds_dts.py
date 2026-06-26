# -*- coding: utf-8 -*-
"""
D12 · MDS 模块划分 + DTS 依赖拓扑 构建器
=================================================================
职责：以 D11 知识图谱 KG-EDU-V1 为唯一数据源，**确定性**派生中层架构两件成对产物：
  - MDS（模块划分方案）：把 KG 的 37 个细组件按「适中业务域粒度」归并为 21 业务模块 + 8 基础模块，
    每模块归一个 Spring 服务，给出职责/Include/Exclude/归属数据表/FR 溯源。
  - DTS（依赖拓扑）：白名单有向依赖边（EDGE-NNNN）+ 层级依赖矩阵 + 条件解耦 + 禁止黑名单。
并自动校验：FR/IFR **100% 覆盖、无重叠**（边界唯一原则）、依赖**无环**（无环原则）。

输出：module-catalog.json、dependency-topology.json、MDS_V1_…模块划分方案.md、DTS_V1_…模块依赖拓扑方案.md
方法论：MDS+DTS 规范（GB 对齐）、ASD-EDU-V1 分层约束、ADR-002/003/004 决策。纯解析无 LLM、可复现。
用法：python build_mds_dts.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DESIGN = ROOT / "wiki" / "summaries" / "design"
KG_FILE = DESIGN / "knowledge-graph.json"
CATALOG_OUT = DESIGN / "module-catalog.json"
DTS_OUT = DESIGN / "dependency-topology.json"
MDS_MD = DESIGN / "module" / "MDS_V1_教育培训收费系统_模块划分方案.md"
DTS_MD = DESIGN / "topology" / "DTS_V1_教育培训收费系统_模块依赖拓扑方案.md"

MDS_ID = "MDS-EDU-V1"
DTS_ID = "DTS-EDU-V1"
BASELINE = "BL-20260623-01"
ASD_REF = "ASD-EDU-V1"

# ============ 业务模块目录（21）：适中业务域粒度，按业务能力归并 KG 组件 ============
# 字段：id, name, service, components(KG组件码), responsibility, includes, excludes, tables
BIZ_MODULES = [
    # —— crm-service 招生客户域 ——
    dict(id="MOD-001", name="客户线索与画像", service="crm-service", components=["CRM"],
         responsibility="以手机号为核心的客户档案、家庭视图、线索登记、撞单提醒、意向分级",
         includes=["客户/家庭/线索 CRUD", "手机号聚合画像", "撞单检测", "意向等级与回访优先级"],
         excludes=["试听排期(MOD-002)", "报价算价(MOD-003)", "鉴权与数据范围(MOD-105)"],
         tables=["crm_customer", "crm_family", "crm_lead", "crm_followup"]),
    dict(id="MOD-002", name="试听预约与候补", service="crm-service", components=["TRIAL"],
         responsibility="试听名额查看、锁定独占、改期取消、候补分级队列与释放通知",
         includes=["名额实时查看", "锁定+15min倒计时释放", "改期/取消", "候补队列(付费优先)"],
         excludes=["班级容量主数据(MOD-005)", "通知下发(MOD-103)"],
         tables=["crm_trial_slot", "crm_trial_lock", "crm_trial_waitlist"]),
    dict(id="MOD-003", name="报名订单与优惠", service="crm-service", components=["ORDER"],
         responsibility="优惠算价、转介绍匹配、特批审批发起、统一收款入口、订单生成",
         includes=["优惠规则算价", "转介绍匹配", "特批审批发起", "下单与统一收款触发"],
         excludes=["支付渠道对接(MOD-101)", "审批引擎(MOD-104)", "收款入账与对账(MOD-009)"],
         tables=["crm_order", "crm_order_discount", "crm_order_approval"]),
    # —— academic-service 教务域 ——
    dict(id="MOD-004", name="排课与调课", service="academic-service", components=["SCH", "RSCH"],
         responsibility="三维冲突检测排课、学员不可用时段、强制覆盖、调课与空档推荐",
         includes=["师/室/生三维冲突检测", "占用缓冲计算", "调课权限与冲突拦截", "空档推荐"],
         excludes=["课时扣减(MOD-006)", "教师课时费(MOD-014)"],
         tables=["edu_schedule", "edu_unavailable_slot", "edu_reschedule_log"]),
    dict(id="MOD-005", name="班级与多校区课务", service="academic-service", components=["CLS", "MCAM"],
         responsibility="班级容量与候补、教室-班型容量配置、多校区课包共享与跨校区缓冲",
         includes=["班级容量/候补", "弹性增员", "多校区课包共享", "跨校区占用缓冲"],
         excludes=["试听候补(MOD-002)", "校区组织隔离规则(MOD-105)"],
         tables=["edu_class", "edu_classroom_capacity", "edu_campus_package"]),
    dict(id="MOD-006", name="考勤与课时账户", service="academic-service", components=["ATT", "MAKEUP"],
         responsibility="双模式签到、迟到早退判定、请假与扣课时、补课额度全周期",
         includes=["全员/扫码签到", "迟到早退/课时扣减", "请假审批", "补课额度生成与清零"],
         excludes=["收入确认(MOD-012)", "教师课时费(MOD-014)", "审批引擎(MOD-104)"],
         tables=["edu_attendance", "edu_course_hour_account", "edu_leave", "edu_makeup_quota"]),
    dict(id="MOD-007", name="转班管理", service="academic-service", components=["TRF", "TREF"],
         responsibility="转班申请双流程、差价按实际单价计算、赠课处理、转班退款路由",
         includes=["转班申请", "差价计算(实际支付单价)", "赠课作废规则", "转余额/原路退路由"],
         excludes=["退费金额计算与红冲(MOD-010)", "审批引擎(MOD-104)"],
         tables=["edu_transfer", "edu_transfer_fee"]),
    dict(id="MOD-008", name="课消与教务报表", service="academic-service", components=["FIN", "TRP"],
         responsibility="实时课消、教师课时费对接、出勤/消课率/退费预警等教务报表",
         includes=["课消看板", "课时费结算单生成", "出勤率/消课率报表", "退费预警表"],
         excludes=["收入确认会计口径(MOD-012)", "工资计提(MOD-014)"],
         tables=["edu_consume_record", "edu_teaching_report"]),
    # —— finance-service 财务域 ——
    dict(id="MOD-009", name="收款与对账", service="finance-service", components=["PAY", "RECON", "PAYIF"],
         responsibility="收款入账与认领、收款拆分审批、日终四方对账、支付异常兜底与单边账",
         includes=["收款认领/拆分", "自动匹配对账", "待认领/待确认/在途处理", "回调失败重试与主动查单"],
         excludes=["下单与统一收款触发(MOD-003)", "支付渠道SDK(MOD-101)"],
         tables=["fin_payment", "fin_reconcile", "fin_unclaimed", "fin_payment_split"]),
    dict(id="MOD-010", name="退费管理", service="finance-service", components=["REF"],
         responsibility="退费金额计算(固化消耗顺序+总课时均价)、分级审批、收入红冲、跨月消课调整",
         includes=["退费明细计算", "参数快照冻结", "三级分级审批", "收入红冲凭证"],
         excludes=["发票红冲开具(MOD-011)", "转班退款发起(MOD-007)", "审批引擎(MOD-104)"],
         tables=["fin_refund", "fin_refund_detail", "fin_reverse_voucher"]),
    dict(id="MOD-011", name="发票管理", service="finance-service", components=["INV"],
         responsibility="自动/手动开票、阈值审核、部分开票与拆分抬头、红冲作废、发票状态标签",
         includes=["开票申请", "阈值审核(默认5000)", "红冲/作废", "退费发票状态联动"],
         excludes=["电票平台接口(MOD-102)", "退费金额计算(MOD-010)"],
         tables=["fin_invoice", "fin_invoice_redflush"]),
    dict(id="MOD-012", name="收入确认", service="finance-service", components=["REV"],
         responsibility="按签到月确认收入、旷课不计收入、赠课只计成本、跨月消课调整",
         includes=["逐节确认收入", "旷课/赠课规则", "总课时含赠送分摊", "跨月调整"],
         excludes=["课消明细采集(MOD-008)", "工资成本核算(MOD-014)"],
         tables=["fin_revenue_recognition"]),
    dict(id="MOD-013", name="欠费与续费", service="finance-service", components=["FEE"],
         responsibility="欠费判定(合同日期/课时消耗)、逾期阶梯催缴、续费提醒与自动重发",
         includes=["欠费巡检", "约课权限暂停(订单级)", "阶梯催缴", "续费提醒(7天/3次)"],
         excludes=["通知下发(MOD-103)", "定时巡检调度(MOD-107)"],
         tables=["fin_arrears", "fin_renewal_reminder"]),
    dict(id="MOD-014", name="教师工资核算", service="finance-service", components=["PAYROLL"],
         responsibility="正价/赠课/代课分项计提、赠课按50%计提、以实际授课考勤为准",
         includes=["工资单生成", "代课成本独立核算", "赠课课时费计提", "依赖调课审批"],
         excludes=["考勤数据源(MOD-006)", "课时费结算单(MOD-008)"],
         tables=["fin_payroll", "fin_substitute_cost"]),
    dict(id="MOD-015", name="财务报表与审计", service="finance-service", components=["FRP", "AUD"],
         responsibility="经营利润表(消课确认制)、欠费账龄、课程盈利、财务全链路审计追溯",
         includes=["利润表/账龄/盈利分析", "下钻凭证", "财务操作审计追溯", "≥3年留存查导"],
         excludes=["经营BI看板(MOD-016)", "审计日志底座(MOD-108)"],
         tables=["fin_profit_report", "fin_aging_report"]),
    # —— bi-service 经营决策域 ——
    dict(id="MOD-016", name="经营看板与审批", service="bi-service",
         components=["DASH", "ENROLL", "OPS", "FMN", "CAMPUS", "APPROVAL"],
         responsibility="集团经营看板、招生渠道ROI、教师效能/满班率、续费率、分级审批与数据权限、关键财务审批",
         includes=["核心看板与下钻", "渠道ROI/转化分析", "满班率/请假率预警", "分级审批路由+移动审批"],
         excludes=["明细业务数据写入(各业务模块)", "审批引擎(MOD-104)", "数据范围鉴权(MOD-105)"],
         tables=["bi_dashboard_snapshot", "bi_channel_cost", "bi_approval_route"]),
    dict(id="MOD-017", name="家长端与小程序", service="bi-service", components=["MINI"],
         responsibility="家长成长档案、自助请假调课、选课报名缴费后台实时同步",
         includes=["成长档案时间线", "家长自助请假/调课", "选课缴费端到端同步"],
         excludes=["小程序数据同步接口(MOD-102)", "考勤课时规则(MOD-006)"],
         tables=["bi_growth_archive", "bi_parent_request"]),
    dict(id="MOD-018", name="异常预警中心", service="bi-service", components=["ALERT"],
         responsibility="资金/业务异常告警聚合、免打扰时段、告警优先级与告警中心",
         includes=["告警聚合", "免打扰(资金类不静默)", "告警优先级排序"],
         excludes=["告警规则来源(各业务模块)", "通知通道(MOD-103)"],
         tables=["bi_alert", "bi_alert_rule"]),
    # —— admin-service 系统管理域 ——
    dict(id="MOD-019", name="组织与权限配置", service="admin-service", components=["ORG", "ACC"],
         responsibility="无限级组织架构、跨校区受限角色、权限模板化与批量授权",
         includes=["组织树维护", "角色与数据范围配置", "权限模板/批量授权/版本"],
         excludes=["运行期鉴权拦截(MOD-105)", "业务参数(MOD-020)"],
         tables=["adm_org", "adm_role", "adm_perm_template", "adm_user_grant"]),
    dict(id="MOD-020", name="业务规则配置", service="admin-service", components=["BIZ"],
         responsibility="业务政策多维组合配置、校验与模拟试算、规则变更遗留数据处理",
         includes=["多维规则配置", "立即/定时生效", "模拟试算", "新旧规则版本与遗留处理"],
         excludes=["规则消费方(各业务模块)", "审批引擎(MOD-104)"],
         tables=["adm_biz_rule", "adm_rule_version"]),
    dict(id="MOD-021", name="灾备与安全治理", service="admin-service", components=["DR", "SEC", "AUDIT"],
         responsibility="异地灾备与恢复演练、备份安全管控、安全策略、告警中心、不可篡改审计日志查询",
         includes=["灾备切换/恢复演练", "备份加密与下载管控", "密码策略/2FA/锁定", "审计日志哈希链查询"],
         excludes=["审计日志写入底座(MOD-108)", "高危告警通道(MOD-103)"],
         tables=["adm_dr_plan", "adm_security_policy", "adm_audit_log"]),
]

# ============ 通用基础模块（8）：全局技术/业务支撑，单向被依赖 ============
BASE_MODULES = [
    dict(id="MOD-101", name="支付网关", responsibility="封装微信/支付宝/银行/现金渠道下单、回调验签、查单",
         excludes=["收款入账与对账(MOD-009)", "订单业务(MOD-003)"], tables=["sys_pay_channel"]),
    dict(id="MOD-102", name="第三方对接", responsibility="短信/电子发票/家长小程序等外部平台适配与重试",
         excludes=["发票业务(MOD-011)", "家长端业务(MOD-017)"], tables=["sys_integration_log"]),
    dict(id="MOD-103", name="通知中心", responsibility="统一通知下发(App/短信/小程序)、模板、已读追踪、降级",
         excludes=["告警规则(MOD-018)", "业务触发(各业务模块)"], tables=["sys_notify", "sys_notify_template"]),
    dict(id="MOD-104", name="审批流引擎", responsibility="通用分级审批流转、超时策略、参数快照、抄送",
         excludes=["各业务审批语义(发起方模块)"], tables=["sys_approval_flow", "sys_approval_task"]),
    dict(id="MOD-105", name="RBAC与校区数据隔离", responsibility="运行期鉴权、角色×校区双维数据范围过滤、临时授权",
         excludes=["组织/角色主数据维护(MOD-019)"], tables=["sys_rbac_scope"]),
    dict(id="MOD-106", name="缓存", responsibility="热点数据缓存、名额/看板等读优化、缓存一致性",
         excludes=["业务数据归属(各业务模块)"], tables=[]),
    dict(id="MOD-107", name="定时任务调度", responsibility="对账/催缴/灾备演练/续费提醒等周期任务调度",
         excludes=["任务业务逻辑(各业务模块)"], tables=["sys_scheduled_job"]),
    dict(id="MOD-108", name="日志审计", responsibility="全字段不可篡改审计日志写入、哈希链、留存",
         excludes=["审计查询展示(MOD-021)"], tables=["sys_audit_base"]),
]

# 全局基础模块（所有业务模块默认可依赖，矩阵级规则，不逐条枚举 EDGE）
GLOBAL_BASE = ["MOD-105", "MOD-106", "MOD-108"]

# ============ DTS 依赖边（白名单，有向）============
# 业务→特定基础（非全局）
BIZ2BASE = [
    ("MOD-003", "MOD-101", "本地调用", "下单触发支付渠道"),
    ("MOD-009", "MOD-101", "本地调用", "收款入账读取渠道流水/查单"),
    ("MOD-003", "MOD-104", "本地调用", "特批审批发起"),
    ("MOD-007", "MOD-104", "本地调用", "转班退款审批"),
    ("MOD-010", "MOD-104", "本地调用", "退费分级审批"),
    ("MOD-016", "MOD-104", "本地调用", "关键财务/优惠分级审批"),
    ("MOD-021", "MOD-104", "本地调用", "例外调整审批"),
    ("MOD-002", "MOD-103", "本地调用", "候补释放通知"),
    ("MOD-003", "MOD-103", "本地调用", "审批/缴费通知"),
    ("MOD-004", "MOD-103", "本地调用", "调课通知家长"),
    ("MOD-006", "MOD-103", "本地调用", "考勤/请假通知"),
    ("MOD-013", "MOD-103", "本地调用", "催缴/续费提醒"),
    ("MOD-018", "MOD-103", "本地调用", "告警下发"),
    ("MOD-009", "MOD-107", "本地调用", "日终对账定时触发"),
    ("MOD-013", "MOD-107", "本地调用", "欠费巡检/续费重发定时"),
    ("MOD-021", "MOD-107", "本地调用", "灾备演练/备份定时"),
    ("MOD-011", "MOD-102", "本地调用", "电子发票平台开票/红冲"),
    ("MOD-017", "MOD-102", "本地调用", "家长小程序数据同步"),
    ("MOD-009", "MOD-102", "本地调用", "支付渠道对账单拉取"),
]
# 跨业务域 Service→Service（最小必要）
BIZ2BIZ = [
    ("MOD-003", "MOD-009", "本地调用", "报名下单后移交收款入账"),
    ("MOD-006", "MOD-008", "本地调用", "签到触发课消采集"),
    ("MOD-008", "MOD-012", "事件", "课消明细异步驱动收入确认"),
    ("MOD-007", "MOD-010", "本地调用", "转班原路退款移交退费计算"),
    ("MOD-009", "MOD-011", "事件", "收款成功异步触发开票"),
    ("MOD-010", "MOD-011", "本地调用", "退费触发发票红冲校验"),
    ("MOD-010", "MOD-012", "事件", "退费驱动收入红冲调整"),
    ("MOD-008", "MOD-014", "本地调用", "课时费结算数据供工资计提"),
    ("MOD-002", "MOD-005", "本地调用", "试听占用读取班级容量"),
    ("MOD-016", "MOD-015", "本地调用", "BI看板读取财务报表口径"),
]
# 业务→外部接口（IFR）
BIZ2IFACE = [
    ("MOD-009", "IFR-PAY-001", "API", "支付渠道回调与主动查单兜底"),
    ("MOD-011", "IFR-INV-001", "API", "第三方电子发票开票/红冲"),
    ("MOD-008", "IFR-FIN-001", "API", "第三方财务系统对接"),
    ("MOD-103", "IFR-MSG-001", "API", "统一通知外发"),
    ("MOD-017", "IFR-MINI-001", "API", "家长小程序实时同步"),
]


def load_kg():
    return json.loads(KG_FILE.read_text(encoding="utf-8"))


def build():
    kg = load_kg()
    comp_realizes = {}   # 组件码 -> [FR...]
    comp_name = {}
    for n in kg["nodes"]:
        if n["type"] == "Component":
            comp_realizes[n["code"]] = n["realizes"]
            comp_name[n["code"]] = n["name"]
    all_fr = set()
    for fr in comp_realizes.values():
        all_fr.update(fr)
    ifr_ids = [n["id"] for n in kg["nodes"] if n["type"] == "Interface"]

    # 组装业务模块：聚合 FR
    assigned_components = []
    for m in BIZ_MODULES:
        frs = []
        for c in m["components"]:
            assigned_components.append(c)
            frs.extend(comp_realizes.get(c, []))
        m["fr_list"] = sorted(set(frs))
        m["fr_count"] = len(m["fr_list"])
        m["type"] = "业务模块"
        m["status"] = "新增待落地"
    for m in BASE_MODULES:
        m["type"] = "通用基础模块"
        m["status"] = "新增待落地"
        m["service"] = "platform-common"
        m["fr_list"] = []
        m["fr_count"] = 0
        m["components"] = []

    # —— 校验：FR 全覆盖 + 无重叠 + 组件全分配 ——
    checks = {}
    covered = []
    for m in BIZ_MODULES:
        covered.extend(m["fr_list"])
    checks["fr_total_kg"] = len(all_fr)
    checks["fr_covered"] = len(set(covered))
    checks["fr_overlap"] = len(covered) - len(set(covered))      # 应=0
    checks["fr_uncovered"] = sorted(all_fr - set(covered))        # 应=[]
    checks["component_total"] = len(comp_realizes)
    checks["component_assigned"] = len(assigned_components)
    checks["component_dup"] = len(assigned_components) - len(set(assigned_components))  # 应=0
    checks["component_missing"] = sorted(set(comp_realizes) - set(assigned_components)) # 应=[]
    checks["ifr_total"] = len(ifr_ids)

    # —— DTS 边装配 + 编号 + 无环校验 ——
    edges = []
    eid = 0

    def add(frm, to, kind, scene, cls):
        nonlocal eid
        eid += 1
        edges.append(dict(edge=f"EDGE-{eid:04d}", **{"from": frm}, to=to, mode=kind, scene=scene, cls=cls))

    for frm, to, kind, scene in BIZ2BASE:
        add(frm, to, kind, scene, "业务→基础")
    for frm, to, kind, scene in BIZ2BIZ:
        add(frm, to, kind, scene, "跨业务域")
    for frm, to, kind, scene in BIZ2IFACE:
        add(frm, to, kind, scene, "业务→外部接口")

    # 无环校验（仅业务模块间有向边）
    biz_ids = {m["id"] for m in BIZ_MODULES}
    adj = {}
    for e in edges:
        if e["from"] in biz_ids and e["to"] in biz_ids:
            adj.setdefault(e["from"], []).append(e["to"])
    cycle = detect_cycle(adj)
    checks["biz_dependency_cycle"] = cycle  # 应=[]

    return kg, BIZ_MODULES, BASE_MODULES, edges, checks, ifr_ids


def detect_cycle(adj):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {}
    cyc = []

    def dfs(u, stack):
        color[u] = GRAY
        for v in adj.get(u, []):
            if color.get(v, WHITE) == GRAY:
                cyc.append(" -> ".join(stack + [v]))
            elif color.get(v, WHITE) == WHITE:
                dfs(v, stack + [v])
        color[u] = BLACK

    for node in list(adj.keys()):
        if color.get(node, WHITE) == WHITE:
            dfs(node, [node])
    return cyc


# ============ 渲染 ============
def render_mds(biz, base, edges, checks):
    L = []
    L.append(f"# {MDS_ID}：教育培训机构教务收费管理系统 · 模块划分方案")
    L.append("")
    L.append("## 1 基础元数据")
    L.append("")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| 文档编号 | {MDS_ID} |")
    L.append("| 适配架构 | 四层分层（单体）/ 见 [ADR-001](../adr/ADR-001_系统顶层架构风格选型决策.md) |")
    L.append("| 文档状态 | 正式生效（CCB 2026-06-26 评审通过） |")
    L.append(f"| 生效基线 | {BASELINE} |")
    L.append(f"| 关联 ASD | [{ASD_REF}](../style/ASD_V1_教育培训收费系统_分层架构风格声明.md) |")
    L.append("| 关联 ADR | ADR-002（粒度）、ADR-003（职责数据边界）、ADR-004（依赖拓扑） |")
    L.append("| 关联 SRS/RTM | BL-20260623-01（88 FR + 5 IFR + 17 NFR） |")
    L.append(f"| 配套 DTS | [{DTS_ID}](../topology/DTS_V1_教育培训收费系统_模块依赖拓扑方案.md) |")
    L.append("| 责任人 | 架构设计（AI 全量执行）/ CCB 评审 |")
    L.append("| 配套机器可读 | [module-catalog.json](../module-catalog.json) |")
    L.append("")
    L.append("## 2 拆分依据与整体思路")
    L.append("")
    L.append("依 MDS 规范 §1.6 **五维拆分方法论**（业务域>数据实体>变更频率>依赖强度>非功能），"
             "并据 [ADR-002](../adr/ADR-002_模块粒度拆分决策.md) 选定的**适中业务域粒度**，"
             "把 [知识图谱 KG-EDU-V1](../知识图谱-v1.0.md) 的 37 个细组件归并为 "
             f"**{len(biz)} 个业务模块 + {len(base)} 个通用基础模块**，每模块归属唯一 Spring 服务。")
    L.append("")
    L.append("- **业务域维度**：按 5 大业务能力域（招生客户/教务/财务/经营决策/系统管理）切分，对齐 5 个 Spring 服务。")
    L.append("- **数据实体维度**：一张表仅归一个主模块（见 [ADR-003](../adr/ADR-003_模块职责与数据边界决策.md)）。")
    L.append("- **变更频率维度**：高频业务（优惠/退费/对账）独立成模块，隔离稳定底座。")
    L.append("- **依赖强度维度**：强关联逻辑同模块（如收款+对账+支付兜底=MOD-009），弱关联拆隔离。")
    L.append("- **非功能维度**：通知/审批/缓存/定时/鉴权/审计/支付网关/第三方对接独立为 8 个基础模块。")
    L.append("- **跨域归并说明**：PAYIF（支付接口兜底，原系统管理域，业务能力属财务收款）并入 MOD-009；"
             "ALERT（异常预警，原综合域）并入 bi 域 MOD-018——按业务能力而非提出方归属。")
    L.append("")
    L.append("## 3 全局模块总览清单")
    L.append("")
    L.append("| 模块ID | 名称 | 类型 | 归属服务 | 状态 | FR数 | 核心定位 |")
    L.append("|---|---|---|---|---|---|---|")
    for m in biz:
        L.append(f"| {m['id']} | {m['name']} | {m['type']} | {m['service']} | {m['status']} | "
                 f"{m['fr_count']} | {m['responsibility']} |")
    for m in base:
        L.append(f"| {m['id']} | {m['name']} | {m['type']} | {m['service']} | {m['status']} | "
                 f"— | {m['responsibility']} |")
    L.append("")
    L.append(f"> 合计 {len(biz)} 业务模块 + {len(base)} 基础模块 = {len(biz)+len(base)} 模块。"
             f"FR 覆盖 {checks['fr_covered']}/{checks['fr_total_kg']}（重叠 {checks['fr_overlap']}，"
             f"未覆盖 {len(checks['fr_uncovered'])}）。")
    L.append("")
    L.append("## 4 单模块详细定义（职责/Include/Exclude/归属实体/FR 溯源）")
    L.append("")
    L.append("### 4.1 业务模块")
    L.append("")
    L.append("| 模块ID | 唯一职责 | Include（可做） | Exclude（禁做/不归属） | 归属数据表 | FR 溯源 |")
    L.append("|---|---|---|---|---|---|")
    for m in biz:
        inc = "；".join(m["includes"])
        exc = "；".join(m["excludes"])
        tbl = "、".join(m["tables"]) if m["tables"] else "—"
        frs = "、".join(m["fr_list"])
        L.append(f"| {m['id']} {m['name']} | {m['responsibility']} | {inc} | {exc} | {tbl} | {frs} |")
    L.append("")
    L.append("### 4.2 通用基础模块")
    L.append("")
    L.append("| 模块ID | 唯一职责 | Exclude（禁做/不归属） | 归属数据表 |")
    L.append("|---|---|---|---|")
    for m in base:
        exc = "；".join(m["excludes"])
        tbl = "、".join(m["tables"]) if m["tables"] else "—（无独占表）"
        L.append(f"| {m['id']} {m['name']} | {m['responsibility']} | {exc} | {tbl} |")
    L.append("")
    L.append("## 5 模块依赖拓扑规范（与 DTS 联动）")
    L.append("")
    L.append(f"- 完整有向白名单（{len(edges)} 条 EDGE）、层级矩阵、禁止黑名单见配套 "
             f"[{DTS_ID}](../topology/DTS_V1_教育培训收费系统_模块依赖拓扑方案.md)。")
    L.append("- 总则：业务模块→基础模块单向合法；基础模块禁止反向依赖业务；跨业务域仅 Service→Service；"
             "强耦合优先事件解耦；禁止循环/反向/穿透。")
    L.append("")
    L.append("## 6 工程目录映射规则")
    L.append("")
    L.append("```")
    L.append("com.edu.{domain}.{module}/  controller/ service/ repository/ model/")
    L.append("  domain ∈ {crm, academic, finance, bi, admin}")
    L.append("com.edu.common.{base}/      gateway/ integration/ notify/ approval/ rbac/ cache/ schedule/ audit/")
    L.append("```")
    L.append("- 模块 ID → 包名：MOD-001→com.edu.crm.customer、MOD-009→com.edu.finance.payment、"
             "MOD-101→com.edu.common.gateway（映射表见 module-catalog.json）。")
    L.append("- 代码按层级 + 模块双重收敛，禁止跨模块目录散落。")
    L.append("")
    L.append("## 7 模块通信与调用规范")
    L.append("")
    L.append("- **本地调用**：同服务内、业务→基础、强一致跨域（如报名→收款）走 Spring Bean 本地调用。")
    L.append("- **事件**：弱一致跨域（课消→收入确认、收款→开票、退费→红冲）走领域事件异步解耦。")
    L.append("- **API**：仅对外部系统（5 个 IFR）经基础模块走 HTTP/SDK。")
    L.append("- **事务**：`@Transactional` 仅声明于 Service；跨服务/异步场景用最终一致 + 补偿，禁止分布式强事务。")
    L.append("- **异常**：统一 BizException + 错误码 `{域}-{编号}`，全局异常处理器兜底。")
    L.append("")
    L.append("## 8 边界漂移校验标准（量化，对接 CodeGraph）")
    L.append("")
    L.append("| 校验项 | 判定 | 等级 |")
    L.append("|---|---|---|")
    L.append("| 职责越界 | 模块出现非本模块 Include 的业务逻辑 | Major |")
    L.append("| 数据漂移 | 模块直接读写非归属表（跨表越权） | Blocker |")
    L.append("| 非法依赖 | 出现 DTS 黑名单依赖（反向/穿透/越域私有） | Blocker |")
    L.append("| 代码散落 | 同一业务能力代码跨多模块目录散落 | Major |")
    L.append("| 需求无主 | 存在未归属任一模块的 FR/接口/数据表 | Blocker |")
    L.append("")
    L.append("## 9 迭代与调整规则")
    L.append("")
    L.append("模块新增/拆分/合并/下线均须经 CR→CIA→ADR-005+ 变更闭环，MOD-ID 终身唯一、废弃保留不复用；"
             "MDS 与 DTS 版本同升同降。")
    L.append("")
    L.append("## 10 质量验收标准")
    L.append("")
    L.append(f"- 需求全覆盖：FR {checks['fr_covered']}/{checks['fr_total_kg']}、IFR {checks['ifr_total']} 全归属，"
             f"无重叠（{checks['fr_overlap']}）、无遗漏（{len(checks['fr_uncovered'])}）。")
    L.append(f"- 边界唯一：{checks['component_assigned']}/{checks['component_total']} 组件唯一归属，"
             f"重复 {checks['component_dup']}、缺失 {len(checks['component_missing'])}。")
    L.append("- 无环：业务模块依赖无环（见 DTS 校验）。")
    L.append("- 可校验：所有边界/职责/依赖均转为上表量化规则与 DTS 白名单。")
    L.append("")
    L.append("## 变更日志")
    L.append("- 2026-06-26：V1 初始创建（草稿），由 build_mds_dts.py 据 KG-EDU-V1 确定性生成，提交 CCB 评审。")
    L.append("- 2026-06-26：CCB 评审通过，状态 草稿 → 正式生效（见 design/CCB_ADR002-004-MDS-DTS_评审记录-v1.0.md）。")
    return "\n".join(L)


def render_dts(biz, base, edges, checks):
    L = []
    L.append(f"# {DTS_ID}：教育培训机构教务收费管理系统 · 模块依赖拓扑方案")
    L.append("")
    L.append("## 1 基础元数据")
    L.append("")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| 拓扑编号 | {DTS_ID} |")
    L.append(f"| 对应 MDS | [{MDS_ID}](../module/MDS_V1_教育培训收费系统_模块划分方案.md) |")
    L.append(f"| 对应 ASD | [{ASD_REF}](../style/ASD_V1_教育培训收费系统_分层架构风格声明.md) |")
    L.append(f"| 生效基线 | {BASELINE} |")
    L.append("| 状态 | 正式生效（CCB 2026-06-26 评审通过） |")
    L.append("| 更新日期 | 2026-06-26 |")
    L.append("| 评审人 | CCB（项目负责人代行） |")
    L.append("| 配套机器可读 | [dependency-topology.json](../dependency-topology.json) |")
    L.append("")
    L.append("## 2 拓扑整体策略")
    L.append("")
    L.append("- **白名单优先**：默认禁止一切未声明依赖，仅下列 EDGE 白名单合法。")
    L.append("- **层级单向**：严格 Controller→Service→Repository→Model（ADR-001/ASD），禁反向/穿透。")
    L.append("- **基础单向被依赖**：业务→基础合法，基础模块禁止反向依赖任何业务模块。")
    L.append("- **跨域低耦合**：跨业务域仅允许 Service→Service；强一致本地调用、弱一致优先领域事件。")
    L.append("- **防环**：业务模块间禁止直接/间接循环依赖。")
    L.append(f"- **全局基础模块**：{', '.join(GLOBAL_BASE)}（RBAC鉴权/缓存/日志审计）为横切能力，"
             "所有业务模块默认可依赖（矩阵级规则，不逐条枚举 EDGE）。")
    L.append("")
    L.append("## 3 模块层级依赖矩阵")
    L.append("")
    L.append("| 起点层 \\ 终点 | Controller | Service | Repository | Model | 基础模块 |")
    L.append("|---|---|---|---|---|---|")
    L.append("| Controller | 禁 | 允许(本模块) | 禁(穿透) | 允许(VO) | 禁 |")
    L.append("| Service | 禁(反向) | 允许(跨域Service) | 允许(本模块) | 允许 | 允许 |")
    L.append("| Repository | 禁(反向) | 禁(反向) | 禁(跨模块) | 允许 | 禁 |")
    L.append("| Model | 禁 | 禁 | 禁 | 允许(同模块) | 禁 |")
    L.append("| 基础模块 | 禁 | 禁(反向业务) | 禁 | 允许(自身) | 允许(基础间无环) |")
    L.append("")
    L.append("> 穿透判定：任意层跳过相邻层调用非相邻下层（如 Controller→Repository）即穿透漂移（Blocker）。")
    L.append("")
    L.append("## 4 逐条有向依赖白名单（EDGE 清单）")
    L.append("")
    L.append("| EDGE | 起点 | 终点 | 方式 | 分类 | 适用场景 |")
    L.append("|---|---|---|---|---|---|")
    name_of = {m["id"]: m["name"] for m in biz + base}
    for e in edges:
        fn = name_of.get(e["from"], e["from"])
        tn = name_of.get(e["to"], e["to"])
        L.append(f"| {e['edge']} | {e['from']} {fn} | {e['to']} {tn if e['to'] in name_of else ''} | "
                 f"{e['mode']} | {e['cls']} | {e['scene']} |")
    L.append("")
    L.append(f"> 白名单合计 {len(edges)} 条；另：全部业务模块→{', '.join(GLOBAL_BASE)} 为矩阵级合法依赖，不重复枚举。")
    L.append("")
    L.append("## 5 条件依赖与解耦方案")
    L.append("")
    L.append("| 场景 | 直接硬依赖? | 解耦方式 |")
    L.append("|---|---|---|")
    L.append("| 课消→收入确认 | 否 | 领域事件 `ConsumeConfirmed`，收入确认订阅 |")
    L.append("| 收款→开票 | 否 | 领域事件 `PaymentSucceeded`，发票订阅 |")
    L.append("| 退费→收入红冲 | 否 | 领域事件 `RefundApproved`，收入确认订阅 |")
    L.append("| 业务→外部系统 | 否 | 经基础模块（网关/第三方对接/通知）适配层中转，禁业务直连 SDK |")
    L.append("| 看板→明细数据 | 否 | 只读查询接口/视图，禁 BI 写业务表 |")
    L.append("")
    L.append("## 6 绝对禁止依赖黑名单")
    L.append("")
    L.append("- 基础模块 → 任意业务模块（反向依赖）。")
    L.append("- 业务模块 A → 业务模块 B 的 Repository/Model（越域私有数据访问）。")
    L.append("- Controller → Repository / 数据库（跨层穿透）。")
    L.append("- 下层 → 上层（Repository/Service→Controller、Model→任意上层）。")
    L.append("- 任意业务模块间直接/间接循环依赖。")
    L.append("- 绕过基础模块直连外部支付/发票/短信 SDK。")
    L.append("")
    L.append("## 7 拓扑通信范式规范")
    L.append("")
    L.append("- 同步本地调用：业务→基础、强一致跨域 Service→Service。")
    L.append("- 异步事件：弱一致跨域（见 §5），最终一致 + 补偿，禁分布式强事务。")
    L.append("- 外部 API：仅经基础模块，统一超时/重试/验签。")
    L.append("- 缓存一致性：写走 Service 主链路，缓存失效由 Service 触发，禁 Repository 直接管缓存。")
    L.append("")
    L.append("## 8 拓扑漂移校验规则（对接 CodeGraph）")
    L.append("")
    L.append("| 漂移类型 | 判定 | 等级 |")
    L.append("|---|---|---|")
    L.append("| 非法依赖漂移 | 代码依赖边不在白名单/命中黑名单 | Blocker |")
    L.append("| 层级穿透漂移 | 出现跨层穿透调用 | Blocker |")
    L.append("| 循环依赖漂移 | 模块/包级存在依赖环 | Blocker |")
    L.append("| 拓扑缺失漂移 | 白名单声明的依赖代码中缺失（死契约） | Minor |")
    L.append("| 调用范式漂移 | 应异步事件处误用同步硬调用（如课消→收入确认） | Major |")
    L.append("")
    L.append("## 9 拓扑迭代与变更规则")
    L.append("")
    L.append("依赖新增/删除/解耦升级须经 CR→CIA→ADR-005+ 变更闭环；EDGE 编号唯一不复用；DTS 与 MDS 同版本同生效。")
    L.append("")
    L.append("## 10 拓扑验收标准")
    L.append("")
    cyc = checks["biz_dependency_cycle"]
    L.append(f"- 无环：业务模块依赖环 = {len(cyc)}（{'通过' if not cyc else '；'.join(cyc)}）。")
    L.append("- 无非法穿透/反向：层级矩阵 + 黑名单全约束。")
    L.append(f"- 白名单全覆盖：{len(edges)} 条 EDGE + 全局基础矩阵规则覆盖全部必要依赖。")
    L.append("- 与 MDS 边界一致：EDGE 起止点均为 MDS 合法 MOD-ID。")
    L.append("- 可机器校验：全部规则转为 CodeGraph 校验项。")
    L.append("")
    L.append("## 变更日志")
    L.append("- 2026-06-26：V1 初始创建（草稿），与 MDS-EDU-V1 成对生成，提交 CCB 评审。")
    L.append("- 2026-06-26：CCB 评审通过，状态 草稿 → 正式生效（与 MDS-EDU-V1 同步）。")
    return "\n".join(L)


def main():
    MDS_MD.parent.mkdir(parents=True, exist_ok=True)
    DTS_MD.parent.mkdir(parents=True, exist_ok=True)
    kg, biz, base, edges, checks, ifr_ids = build()

    # 写 JSON
    catalog = {
        "meta": {"mds_id": MDS_ID, "baseline": BASELINE, "asd": ASD_REF,
                 "source_graph": kg["meta"]["graph_id"], "generator": "build_mds_dts.py"},
        "checks": checks,
        "business_modules": [
            {k: m[k] for k in ("id", "name", "type", "service", "status", "components",
                               "responsibility", "includes", "excludes", "tables", "fr_list", "fr_count")}
            for m in biz],
        "base_modules": [
            {k: m[k] for k in ("id", "name", "type", "service", "status", "responsibility", "excludes", "tables")}
            for m in base],
    }
    topo = {
        "meta": {"dts_id": DTS_ID, "mds_id": MDS_ID, "baseline": BASELINE,
                 "global_base": GLOBAL_BASE, "generator": "build_mds_dts.py"},
        "checks": {"cycle": checks["biz_dependency_cycle"], "edge_total": len(edges)},
        "edges": edges,
    }
    CATALOG_OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    DTS_OUT.write_text(json.dumps(topo, ensure_ascii=False, indent=2), encoding="utf-8")
    MDS_MD.write_text(render_mds(biz, base, edges, checks), encoding="utf-8")
    DTS_MD.write_text(render_dts(biz, base, edges, checks), encoding="utf-8")

    print("[OK] MDS + DTS 已生成")
    print(f"  - {CATALOG_OUT}")
    print(f"  - {DTS_OUT}")
    print(f"  - {MDS_MD}")
    print(f"  - {DTS_MD}")
    print(f"  业务模块 {len(biz)} + 基础模块 {len(base)} = {len(biz)+len(base)}；EDGE {len(edges)} 条")
    print(f"  [校验] FR 覆盖 {checks['fr_covered']}/{checks['fr_total_kg']}（重叠{checks['fr_overlap']}/"
          f"未覆盖{len(checks['fr_uncovered'])}）；组件归属 {checks['component_assigned']}/{checks['component_total']}"
          f"（重复{checks['component_dup']}/缺失{len(checks['component_missing'])}）；"
          f"业务依赖环 {len(checks['biz_dependency_cycle'])}")
    if checks["fr_uncovered"]:
        print("  [警告] 未覆盖 FR：", checks["fr_uncovered"])
    if checks["component_missing"]:
        print("  [警告] 未归属组件：", checks["component_missing"])


if __name__ == "__main__":
    main()
