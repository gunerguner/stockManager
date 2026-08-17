---
name: stockmanager-project
description: stockManager 个人股票交易记录项目参考：Django 6 + Umi 4 架构、雪球盈亏公式、沪深/港股行情与汇率、关注列表、Redis 缓存失效、行情源、SQLite、Docker 三服务部署。在 stockManager 仓库内改功能、修 bug、加 API、动缓存/行情/前端页面或 Docker 时使用。
disable-model-invocation: false
---

# stockManager 项目参考

个人持仓与盈亏记录工具（雪球公式），覆盖沪深 A 股 / 北交所 / 港股通；股票代码用小写前缀，如 `sh600519`、`sz000001`、`bj430047`、`hk00700`（港股按 HKD/CNY 汇率换算为人民币口径）。

## 仓库布局

```
stockManager/                 # Git 根
├── README.md / README.zh-CN.md
├── install.sh
├── docker/
└── stockManager/             # 应用根（注意嵌套同名目录）
    ├── manage.py
    ├── stockManager/         # Django 项目：settings.py、urls.py
    ├── backend/              # 唯一 Django app
    │   ├── datasource/       # 外部行情适配（最底层）
    │   ├── common/           # web/ + domain/ + types/utils/cache/constants
    │   ├── services/         # app/ + cache/ + calculation/ + data_sync/
    │   ├── views/ / admin/ / models/
    │   └── ...
    ├── front/                # Umi 4 + Ant Design Pro
    ├── requirements.txt
    └── db.sqlite3
```

版本：`stockManager/stockManager/__init__.py` 与 `front/package.json`（当前 **1.0.0**）。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python ≥3.13，Django **6.x**，Gunicorn（Docker） |
| 前端 | Umi Max **4.6**，**Utoopack**（`utoopack: {}`，`mfsu: false`），React **19**，antd **6**，utoo（`ut`），Node ≥20 |
| 缓存 | Redis + `django-redis`（逻辑 key 前缀由 Django 管理） |
| 数据库 | **SQLite** 仅此一种 |
| 行情 | `easyquotation` **tencent**（沪深实时）+ 腾讯 `sqt.gtimg.cn`（港股实时）；`baostock`（仅 A 股除权除息）；百度 opendata（PE/PB）；腾讯 gtimg（历史高，统一 qfq）；sina 外汇（HKD/CNY） |
| 日历 | `exchange_calendars` **XSHG / XHKG**（`common/domain/calendar.py`，CN/HK 分市场；前端右上角交易状态 Tag 走 `/api/tradingStatus`，后端统一计算） |

## 架构要点

**请求路径**：Umi SPA → `/api/*` → `backend.views` → `services/app/integrate.py`（门面）→ `cache/` / `calculation/` / `data_sync/`；回源走 `backend/datasource/`。

**分层**（依赖只向下）：

| 层 | 包 | 说明 |
|----|----|------|
| Infra | `backend/datasource/` | 外部数据源适配（`realtimePrice`/`baostock_source`/`baiduValuation`/`exchangeRate`/`historicalHigh`/`historicalDaily`/`http_client`）；仅拉取与标准化 |
| L2 | `services/cache/` | Redis：`repository` 门面 + `keys` + `refresh` + `user/` + `market/`；逻辑 key、TTL、失效、回源 `datasource` |
| L2 | `services/data_sync/` | 日频缺口补拉并写入 SQLite（`StockDailyPrice` / `HkdCnyDailyRate`）；**不**碰 Redis |
| L3 | `services/calculation/` | 纯计算：`holdings/`（盈亏）、`nav/`（净值回放/指标）；**不**依赖 cache / data_sync / datasource |
| L4 | `services/app/` | 用例编排：`integrate`、`dividend`、`nav`、`watchlist` |
| Shared | `backend/common/` | `web/`（HTTP）、`domain/`（交易原语）、根级 `types`/`utils`/`cache`/`constants` |

**统一响应**：`json_response(status, data, message)`，`ResponseStatus`：SUCCESS=1、ERROR=0、UNAUTHORIZED=401。装饰器：`@require_authentication`、`@require_superuser`、`@handle_exception`、`@parse_json_body`。

**认证**：Session + CSRF；前端 `credentials: 'include'`（`front/src/services/api.ts`）。

**读路径（持仓列表）**：
1. `GET /api/stocks` → `Integrate.get_calculated_result`
2. 缓存命中 → 返回 `CalculatedResult`（含 `stocks` / `overall` / `markets`）
3. 否则：加载 `Operation` → `CacheRepository.load_calculation_inputs`（聚合现金流、汇率、行情 `market/prices.query_prices`→`fetch_prices`、元数据、各市场状态）→ `Calculator.calculate_stock_list` → `calculate_overall` → 写缓存

**写后失效**：信号在 `cache/` 内（**非** `app/integrate.py`）。`cache/user/store.py` 的 `post_save`/`post_delete` 清 `Operation` / `CashFlow` / `Info`（仅 `INCOME_CASH`）用户缓存；`cache/market/meta.py` 清 `StockMeta` 全量元数据；`cache/user/watchlist.py` 清 `WatchItem` 关注列表缓存。

```mermaid
flowchart LR
  Umi[Umi :8001] -->|proxy /api| Django[Django :8000]
  Django --> SQLite[(SQLite)]
  Django --> Redis[(Redis)]
  Django --> Quote[tencent A股 + sqt 港股]
  Django --> Baostock[baostock 除权除息]
  Django --> Baidu[百度 opendata PE/PB]
  Django --> FX[港股 HKD/CNY 汇率]
```

## 业务域（已实现）

| 域 | 关键文件 |
|----|----------|
| 交易记录 | `backend/models/` → `Operation`（BUY/SELL/DV；港股通买卖 `price` 为 HKD、`amount` 为实际 CNY 成交额、`fee` 为 CNY） |
| 盈亏计算 | `backend/services/calculation/holdings/`（雪球规则，含 XIRR） |
| 净值分析 | `calculation/nav/`（纯回放）+ `services/data_sync/`（日频价/汇率补拉）+ `services/app/nav.py`（编排写库）+ `GET/POST /api/nav*` |
| 组合汇总 | `backend/common/types.py` → `OverallData` |
| 资金流水 | `CashFlow`（存取）；`Info.INCOME_CASH`（如逆回购收益） |
| 股票元数据 | `StockMeta`（SH60、SZ00、SZ300、SH688、BJ、CONV、FUNDIN、FUNDAB、HK、OTHER） |
| 除权除息 | `backend/services/app/dividend.py` + `POST /api/dividend`（仅 A 股自动生成；港股分红在 Admin 手动录入 DV，`cash` 为每股 CNY 到账） |
| 实时价 | `backend/datasource/realtimePrice.py`（`fetch_prices`，沪深+港股） |
| 关注列表 | `WatchItem` + `services/app/watchlist.py`（`build`/`set_hidden`）+ `cache/user/watchlist.py` + 前端 `pages/Watch/` |
| 估值 PE/PB | `datasource/baiduValuation.py`（`fetch_pe_pb`）+ `cache/market/valuation.py` |
| 历史高价 | `datasource/historicalHigh.py`（gtimg 周线 qfq）+ `cache/market/hist_high.py` |
| 港股/汇率 | `common/domain/market.py`（CN/HK 抽象）、`common/domain/settlement.py`（CNY 资金账 + 原币展示账）、`datasource/exchangeRate.py` + `cache/market/fx.py`（即期 `fx:hkd_cny`）+ `data_sync/daily_fx.py`（净值日频牌价） |
| 缓存 | `services/cache/` + `common/cache.py`；详见 [references/cache.md](references/cache.md) |

**股票代码**：小写交易所前缀 + 代码，如 `sh600519`、`sz000001`、`bj430047`、`hk00700`。后端将港股严格识别为 `hk` + 5 位数字；录入以此规则为准。

**港股通口径**：`price`、每股成本为 HKD；港股 BUY/SELL 的 `amount` 为实际 CNY 成交额、`fee` 为 CNY。市值、盈亏、组合汇总和 XIRR 均为 CNY；**当前**市值按即期 HKD/CNY 换算，成交时的 CNY 金额不随汇率重算；**净值历史回放**按日频中行牌价折算港股市值。

## 修改导航（最常改哪里）

| 目标 | 改动位置 |
|------|----------|
| 新 API | `backend/views/`（仅 `stock.py` / `user.py`）→ `backend/urls.py` → `front/src/services/api.ts` |
| 新计算字段 | `calculation/holdings/`（`calculator`/`overall`/`single_stock`/`single_metrics`）+ `common/types.py` → `StockList` / `ProfitAnalysis` / `Transaction` 页面；港股结算口径同时检查 `common/domain/settlement.py` |
| 缓存逻辑 | `services/cache/`（`repository` 门面 + `user/` + `market/`）；先读 [references/cache.md](references/cache.md)；失效信号在 `cache/user/store.py`、`cache/market/meta.py`、`cache/user/watchlist.py` |
| 行情/估值/汇率 | `backend/datasource/`（`realtimePrice`/`baiduValuation`/`exchangeRate`/`historicalHigh`/`baostock_source`），缓存编排在 `cache/market/`；日频补拉在 `services/data_sync/` |
| 关注列表 | `models.WatchItem` → `cache/user/watchlist.py` → `app/watchlist.py` → `views/stock.watchlist` → 前端 `pages/Watch/` |
| 净值 | `calculation/nav/` + `data_sync/` + `app/nav.py` → `/api/nav`、`/api/nav/refresh` → 前端 `pages/NavAnalysis/` |
| 数据库 | `models/` → `makemigrations` → `migrate` → `backend/admin/` |
| 新前端页 | `front/config/routes.ts` + `src/pages/`；权限 `access.ts` |
| 价格展示 | `front/src/utils/format/stock.ts`（`formatMarketPrice` / `formatAmount` / `isHkCode`） |
| 部署/静态 404 | 改 Umi 后须 **重建 frontend 镜像**；见 `docker/nginx.conf` |

## 快速决策树（先定位再改）

- **症状：接口 401/403、登录态异常**
  - 先看：`backend/views/user.py`、`backend/common/web/decorators.py`
  - 再看：`front/src/services/api.ts` 是否保留 `credentials: 'include'`
- **症状：持仓页慢/数据不刷新**
  - 先看：`backend/services/app/integrate.py`（是否命中缓存）
  - 再看：`backend/services/cache/`（TTL 与 key）
  - 再看：`backend/datasource/realtimePrice.py`（行情源与交易时段）
- **症状：改了前端但线上没变化**
  - 先做：`docker compose build frontend && docker compose up -d frontend`
  - 原因：仅 frontend 镜像包含 Umi 构建产物
- **症状：新增字段前端拿不到**
  - 先看：`backend/common/types.py` 与 `calculation/holdings/` 是否同步
  - 再看：`front/src/services/api.ts` 的类型定义与页面消费

## 本地开发

| 终端 | 命令 | 端口 |
|------|------|------|
| 后端 | `cd stockManager && python manage.py runserver` | **8000** |
| 前端 | `cd stockManager/front && ut run dev` | **8001**（代理 `/api` → 8000） |

需 Redis。`install.sh` **不**执行 `ut run build`。

**环境变量**（`stockManager/stockManager/.env`）：`DJANGO_SECRET_KEY`、`DJANGO_DEBUG`、`REDIS_URL`。Docker 另见 `SQLITE_PATH`、`CSRF_TRUSTED_ORIGINS_EXTRA` 等（`docker/.env.example`）。

**前端环境**：`UMI_ENV=dev|test|pre` → `config/config.{env}.ts`；生产 `publicPath: '/static/'`。

## Docker 部署要点

- 三服务：**redis**、**backend**（仅 API）、**frontend**（`ut run build` + Nginx **8080**）
- **仅 frontend 镜像**含 Umi 构建产物；只重建 backend **不会**更新页面
- Nginx 反代 `/api/`、`/sys/admin/` 到 backend:8000
- 与 carSales 同机部署时设 `COMPOSE_PROJECT_NAME=stockmanager`

## API 一览

| 方法 | 路径 | 权限 |
|------|------|------|
| GET | `/api/operations` | 登录用户 |
| GET | `/api/stocks` | 登录用户 |
| GET | `/api/watchlist` | 登录用户 |
| POST | `/api/watchlist/hidden` | 登录用户 |
| GET | `/api/tradingStatus` | 公开（行情日历） |
| GET | `/api/nav` | 登录用户 |
| POST | `/api/nav/refresh` | 登录用户 |
| POST | `/api/dividend` | 登录用户 |
| POST | `/api/updateIncomeCash` | 登录用户 |
| POST | `/api/clearCache` | superuser |
| POST | `/api/login` | 公开 |
| POST | `/api/logout` | 登录用户 |
| GET | `/api/currentUser` | 登录用户 |

Django Admin：`/sys/admin/`（`canAdmin` 用户从头像菜单新窗口打开；**无**独立 `/admin` 前端路由）。

## 测试

**无自动化单元测试**。改完后手动验证：登录 → `/list` 持仓 → `/profit-analysis` 盈亏归因 → `/transaction` 交易数据 → `/nav-analysis` 净值 → 除权刷新 →（管理员）清缓存。前端可跑 `ut run lint`、`ut run type-check`。

建议最小检查集（改动后至少执行其一）：

1. 仅后端改动：`python manage.py check`
2. 仅前端改动：`ut run type-check`
3. API/计算改动：手动走通 `/list` + `/profit-analysis` + `/transaction` + `/nav-analysis` + `/api/clearCache`

## 编码约定

- 编排/计算类用 **classmethod**（`Integrate`、`Calculator`、`StockHold`、`Dividend`、`CacheRepository`、`NavAnalysis`），无重度 DI；行情/汇率/缓存 store 层为**模块级函数**（如 `fetch_prices`、`market.prices.query_prices`、`market.fx.get_hkd_cny_rate`）
- 模型/API JSON 字段多为 **camelCase**（`operationType`、`stockType`）
- 共享工具在 `backend/common/`：根级 `cache.py` / `types.py` / `constants.py` / `utils.py`；`web/`（装饰器、响应、认证）；`domain/`（`market` CN/HK 抽象 ≠ `datasource`、`calendar`、`settlement`、`operations`）
- 依赖方向：`app → calculation / cache / data_sync / datasource`；`cache → datasource`；`data_sync → datasource / common.domain`；`calculation` 与 `datasource` / `cache` / `data_sync` 互不依赖；`common.web` 与 `common.domain` 互不引用；`common` 不依赖 `services` / `datasource`
- 语言与时区：`zh-hans`、`Asia/Shanghai`
- 用户角色：`admin`（superuser）| `staff` | 普通用户（`access` 为空字符串）；前端 `access.ts` 控制 `canAdmin`

## 提交前自检清单（防回归）

- 是否新增/修改 API：`backend/urls.py` 与 `front/src/services/api.ts` 是否同时更新
- 是否修改模型：是否完成 `makemigrations` 与 `migrate`，并检查 admin 展示
- 是否修改计算字段：`common/types.py`、`calculation/holdings/`、前端页面字段是否三处一致
- 是否修改缓存：是否覆盖写后失效路径（`Operation` / `Info` / `CashFlow` / `StockMeta` / `WatchItem`）
- 是否修改前端路由或静态资源：是否验证 Docker frontend 重建流程

## 深度参考（按需阅读）

| 场景 | 文档 |
|------|------|
| 路径索引 / 部署 / 迁移 / 排障 | [references/reference.md](references/reference.md) |
| 缓存 key / TTL / 失效 / 交易时段刷新 | [references/cache.md](references/cache.md) |
| 外部数据源 / datasource 层 / 失败行为 | [references/external-data.md](references/external-data.md) |
| 前端主题 / 明暗切换 / 盈亏颜色 / less | [references/theme.md](references/theme.md) |
