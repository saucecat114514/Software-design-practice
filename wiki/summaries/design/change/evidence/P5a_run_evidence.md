# P5a 运行证据 · 持久化底座（H2 + MyBatis）

> 留痕：CR-EDU-2026-0001 / P5a。本地实跑，证明退费/转班模块由内存仓库改 MyBatis+H2 后端到端可运行。
> 运行方式：`java -cp "target/classes;<deps>" com.edu.EduChargeApplication`（H2 嵌入式，零外部依赖）。

## 一、启动成功
```
o.s.b.w.embedded.tomcat.TomcatWebServer : Tomcat initialized with port 8080 (http)
o.s.b.w.embedded.tomcat.TomcatWebServer : Tomcat started on port 8080 (http) with context path ''
com.edu.EduChargeApplication            : Started EduChargeApplication in 2.382 seconds
```
schema.sql 建表 + data.sql 种子自动执行（spring.sql.init），无启动异常。

## 二、接口实跑（数据来自 H2，非内存）

**1) 退费计算** `POST /api/refund/v1/calc/create` `{"order_id":"ORD-20260301-0012","reason":"relocation"}`
```json
{"code":"0000","message":"成功","data":{"purchased_hours":100,"gift_hours":20,"consumed_hours":25,
"avg_unit_price":100.00,"gift_discount_factor":1.0,"refund_amount":9500.00,"snapshot_id":"RFS-ORD-20260301-0012"},
"timestamp":"2026-06-29T20:29:53+08:00"}
```
→ MyBatis 读 `fin_order_snapshot`（record 映射成功）+ MERGE 存 `fin_refund`；金额 9500（v1 口径正确）。

**2) 退费审批** `POST /api/refund/v1/approve/update` `{"refund_id":"REF-ORD-20260301-0012","action":"approve","principal_approver":true}`
```json
{"code":"0000","message":"成功","data":{"refund_status":"APPROVED","approval_level":"level2","auto_passed":false}}
```
→ findById 读回上一步 MERGE 的退费单（**存取往返通过**）；9500 → level2 分级正确。

**3) 转班费用** `POST /api/transfer/v1/fee/confirm` `{"order_id":"ORD-20260601-0007","target_class_id":"CLS-A2","gift_handle_mode":"void"}`
```json
{"code":"0000","message":"成功","data":{"actual_unit_price":245.00,"remaining_value":4900.00,
"target_amount":6000.00,"diff_amount":1100.00,"gift_voided":true}}
```
→ MyBatis 读 `edu_transfer_snapshot` + `edu_transfer_target_price`（record 映射成功）；差价 1100 正确。

## 三、回归校验
持久层重构后逆向校验：39 类，**违规 0（Blocker 0 / Major 0 / Minor 0），关键漂移 0**（满足 CCB 要求"持久层重构后立即逆向校验+冒烟"）。

## 四、踩坑记录
- 首跑 `mvn spring-boot:run` 失败：① 新增依赖 jakarta.xml.bind-api 下载握手中断（网络抖动，重试解决）；② `-o` 离线模式下 spring-boot 插件自身依赖（loader-tools 等）未缓存——改用 `mvn dependency:build-classpath` 导出 classpath 后 `java -cp` 直接跑主类，绕开插件。
- 退费首测报 SYS-0500（JSON parse 0xb0）：git-bash 发中文 `reason` 编码坏，非代码 bug；改 ASCII 后通过。
