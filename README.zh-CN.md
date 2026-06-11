**语言 / Languages：** [English](README.md) | [简体中文](README.zh-CN.md)

炒股多年，一直苦于没有一个特别让我满意的股票交易记录软件，于是花了点时间写了一个类似的工具，同时也学习了一些相关的知识。

# 效果如下

## 持仓盈亏

![image.png](https://s21.ax1x.com/2025/10/27/pVxFACd.png)

## 数据分析

![image.png](https://s21.ax1x.com/2025/10/27/pVxFF4H.png)

## 除权更新

![image.png](https://s21.ax1x.com/2025/10/27/pVxFiUe.png)

主要的特点包括：

- 完整而精确的个股、整体数据指标。
- 完整的个股操作记录。
- 自动生成除权除息记录。
- 准确的个股排序功能。
- 支持港股通：个股港币 `$` 展示，总资产按 HKD/CNY 即期折算为人民币。
- 极简界面，无广告，无妖艳的干扰元素。

# 技术方案

## 后端

如果要搭建一个简单的Web api技术方案其实很多，我在2010年左右了解django，21年开始这个项目的时候就选择了它，其实选别的方案也没问题，能快速落地就行。数据的获取和计算，使用Python也非常方便。

数据库使用sqlite，我们需要存储的数据很少，就用了最轻量级调试最方便的方案。

## 前端

初版中前端采用Vue + element-ui的方案，后续切换到了umijs + antd 的方式。

我之前的前端代码写得不多，在实际编码的时候，还是花了一点时间去学习框架和处理交互视觉问题。二期工作中主要重点也在前端，优化了页面的视觉和体验。

## 数据源

实时交易指标来自腾讯接口，通过 [easyquotation](https://github.com/shidenggui/easyquotation) 库获取。支持股票、场内基金、可转债等产品，接口地址 `http://qt.gtimg.cn/q=`。

历史除权除息数据来自 [BaoStock](http://baostock.com/baostock/index.php)（仅 A 股；港股不支持）。估值 PE/PB、历史高价等已改用百度 opendata 与腾讯 gtimg，不再经 baostock。

## AI辅助

2025年我使用AI对项目做了代码的优化和依赖的升级，效果非常好。我比较大的一个体会是，学习一个技术的方式被完全改变了，基本我想要什么，只要用提示词都能得到，略过了痛苦的自己排查、查询资料的过程。如果我们看最终的结果，这无疑是一个提效，但对于年轻的学习者来说未必是一个好事。

## 数据指标

所有的计算公式来自雪球：

```
1、成本价
持股数 = ∑买入数量 + ∑红股数量 + ∑拆股所增数量 - ∑卖出数量 - ∑合股所减数量
摊薄成本 = (∑买入金额 - ∑卖出金额 - ∑现金股息) / 持股数
持仓成本 = ∑买入金额 / (∑买入数量 + ∑红股数量 + ∑拆股所增数量 - ∑合股所减数量) 

2、浮动盈亏
浮动盈亏额 ＝ (当前价 - 持仓成本) * 多仓持股数
浮动盈亏率 ＝ 浮动盈亏额 / (持仓成本价 * 持股数)
分市场浮动盈亏额 ＝ ∑个股浮动盈亏额
分市场浮动盈亏率 ＝ 分市场浮动盈亏额 / ∑(个股持仓成本 * 个股持股数)

3、累计盈亏
个股累计盈亏额 ＝ 多仓市值 - (∑买入金额 - ∑卖出金额 - ∑现金股息) 

4、当日盈亏
昨日市值 > 0
当日盈亏额 = (现市值 - 昨收市值 + 当日∑卖出 - 当日∑买入)
当日盈亏率 = 当日盈亏额 / (昨市值 + 当日∑买入 + 当日∑卖空)
昨日市值 = 0
当日盈亏额 = (现价 - 持仓成本) * 股数 + 当日∑卖出 - 当日∑买入
当日盈亏率 = 当日盈亏额 / 当日∑买入
现金 = 本金+累计盈亏-市值
```

比较坑爹的是，一个股票持仓成本计算的时候，只计算清仓后最近一次开始的持股成本。

这块计算花了我整整一个下午的时间来做，有很多小逻辑细节，都体现在了代码里。

## 数据迁移

个人交易的数据可以从券商的软件获取，如果之前在别的平台有记录也可以做导出。

我在想导出的时候发现我的券商没有Mac的客户端，于是我果断去了离家最近的网鱼网咖，在一堆社会人打游戏的叫骂中，胆战心惊地安装券商软件，导出了所有的股票交易记录...即使如此，表格的解析，数据的校对极其繁琐耗时，也是整个工作中最花时间的地方。

# 搭建方式

## 手动搭建（前后端分离开发）

1. 安装 Python(版本>=3.13)、pip、git、redis。
2. 使用 pip 安装依赖（`requirements.txt`）。
3. 安装 Node(版本>=20)、utoo（`npm install -g utoo`）。
4. git clone：https://github.com/gunerguner/stockManager
5. 进入 `stockManager/front`，执行 `ut install`（**无需** `ut run build`）。
6. 在 `stockManager` 目录创建 `.env`：`cp stockManager/.env.example stockManager/.env`，`DJANGO_SECRET_KEY` 可用  
   `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` 生成。
7. `python manage.py makemigrations`、`python manage.py migrate`（或直接复制数据库文件）。
8. `python manage.py createsuperuser` 创建管理账号。
9. 启动 Redis：`redis-server`。
10. **两个终端启动：**
    - 终端 1（`stockManager` 目录）：`python manage.py runserver` → API 与 Admin 在 **8000**
    - 终端 2（`front` 目录）：`ut run dev` → 业务前台在 **8001**（`/api/` 代理到 8000）

- 业务前台：http://127.0.0.1:8001
- 管理后台：http://127.0.0.1:8000/sys/admin/

## 自动搭建

执行 `./install.sh`（仅安装依赖，不构建前端产物）。

# 部署方式

1. **Docker（推荐）**：前端仅在 `frontend` 镜像构建一次；后端镜像不含 Umi 产物。见 [docker/README.md](docker/README.md)。
2. 传统部署：Nginx 托管 `front/dist` 并反代 API；后端仅 Gunicorn + Django Admin 静态。

# 项目故事

项目开始与2020年，2021年第一次重构并在云服务器部署，在后续使用过程中发现了大量bug并做了修复。它伴随我走过了20、21两年的小牛市和后续3年多漫长的熊市。

因为工作繁忙，生活不易，很长一段时间我都没有更新项目。

2025年底，终于有了时间做一点自己喜欢的事情，于是重新开始投入这个项目，后续争取保持每年更新。
