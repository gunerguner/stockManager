# 前端样式从 less / 内联 style 迁移到 antd 组件 `styles` 属性 —— 方案

> 范围：`stockManager/front/`（Umi Max 4 + React 19 + antd **6.3.6**）
> 背景：antd 6 为多数组件提供了 **`styles` 属性**（per-slot 对象，如 `styles={{ body, header, content }}`），可直接在组件上注入分槽样式，跟随主题 token 热切换，无需 `.less` 与 `:global` 深选择器。
> 目标：盘点哪些 less / 内联 style 可以改用 `styles` 实现，给出**优先级、可行性、改造方式**，本文档**仅产出方案，不修改代码**。

---

## 一、结论速览（TL;DR）

| 可改造性 | 说明 | 涉及文件 |
|---------|------|---------|
| ✅ **强烈建议改造** | 纯 antd 组件分槽样式，`styles` 直接覆盖，收益大、风险低 | `Account`、`Common/modal`、`CostList` 中 Statistic |
| ⚠️ **部分可改造** | antd 组件分槽可改 `styles`，但含伪类/媒体查询/嵌套结构，部分需保留 less | `OverallBoard`、`HoldingsList`、`AnalysisList`、`RightContent`、`Login` |
| 🚫 **不建议改造** | 全局 reset / ProLayout 内部类 / 跨组件 `:global` 覆盖 / 复杂响应式 | `global.less`、`variables.less`、`Login` 品牌区、`RightContent` 头部布局 |

**核心原则**：`styles` 属性只能覆盖**单一组件的具名 slot**，凡是涉及「伪类（`:hover`/`&:last-child`）」「媒体查询（`@media`）」「穿透子组件（`:global .ant-table-thead`）」「全局 reset」的场景，**仍需 less**。改造应聚焦于「这个 class 名其实只装饰一个 antd 组件的某个 slot」的情况。

---

## 二、现状盘点

### 2.1 less 文件清单（共 10 个）

| 文件 | 主要职责 | 复杂度 |
|------|---------|--------|
| `styles/variables.less` | 全局 less 变量（`@primary-color` 等），由 `config.ts` 注入 | 全局，**不动** |
| `global.less` | reset、ProLayout 背景色、移动端全局表格/Modal/ProCard 适配 | 全局，**不动** |
| `components/RightContent/index.less` | 顶部右侧操作区 `.right`、`.action` hover、`.dark` 头像背景 | 中 |
| `components/Common/index.less` | `.page-container`、`.table-list-wrapper`、`.table-list-header`、`.stock-group-link`、`.watch-detail-descriptions` | 中（多页共用） |
| `components/Common/modal/index.less` | Modal 内 `.modal-info-row`、`.common-table-header`、`.stock-header-wrapper` 等结构类 | 高（含 BEM + `:global` + dark） |
| `pages/Account/index.less` | 账户卡片：`.card`/`.header`/`.avatar`/`.name`/`.table`/`.row`/`.label`/`.value` | 中 |
| `pages/Login/index.less` | 登录页品牌区 + 表单卡片布局，含 `@media` | 高 |
| `pages/ProfitAnalysis/components/index.less` | 仅移动端表格列宽 `nth-child` | 低（纯 `:global`） |
| `pages/StockList/components/index.less` | `.holdings-list-wrapper` sticky 表头 + `.overall-board-wrapper` 展开分割线 hover | 高 |
| `pages/Transaction/components/index.less` | `.cost-list-wrapper` 及大量 BEM（`year-card`/`month-card`/`metric-card`） | 高（含 `@media` + 复杂结构） |

### 2.2 内联 `style` 与 `styles={{}}` 使用现状

- **已在用 `styles` 属性**（5+ 处）：`Account` Card body、`OverallBoard` Statistic/Divider、`CostList`/`AnalysisList` Statistic（经 `getHeaderStatisticStyles`）、`useCommonModal` 的 Modal `styles`、`Tooltip styles={{ container }}`、`useCommonModal` Table 移动端 `styles={{ body:{row}, header:{row} }}`。
- **大量内联 `style={{ color: token.xxx }}`**：`CostList`（`metric-card`、`month-card`、`year-card` 全靠内联 token 上色）、`OverallBoard`（CSS 变量注入）。
- 说明项目已有「token + 内联 style + `styles` 属性」的混合范式，迁移是顺势收口。

---

## 三、逐页面 / 组件改造方案

### 3.1 ✅ Account 页面 —— **强烈建议改造**

`pages/Account/index.tsx` + `pages/Account/index.less`

**现状**：用 8 个 less class 装饰 Card 内的 header / avatar / 自绘「键值表」。

**可改造点**：

| less class | 改造方式 | 备注 |
|-----------|---------|------|
| `.card`（max-width/margin/border-color） | `Card` 已有 `className`；或改 `Card styles={{ body:{...} }}` + 外层 div 控制宽度。`border-color` 可直接走 token 不写 | 部分 |
| `.header`（flex 布局） | 换成 `<Space>` 或内联 style | ✅ |
| `.avatar`（bg/color） | `Avatar style={{ backgroundColor: token.colorPrimary, color:'#fff' }}` | ✅ |
| `.name` / `.username` | `<Typography.Text>` + `style` 或 `type="secondary"` | ✅ |
| `.table`/`.row`/`.label`/`.value` | 这是**自绘键值表**（非 antd Table）。建议直接换成 **`Descriptions` 组件**，用 `styles={{ label:{...}, content:{...} }}` 或 `column` 属性，彻底删除自绘结构 | ✅✅ 收益最大 |

**改造后**：`Account/index.less` 可**整文件删除**（保留 `@import '@/components/Common/index.less'` 的 `page-container` 即可，或外层用 Common）。

**预估工作量**：小。核心是把自绘键值表换成 `Descriptions`。

---

### 3.2 ✅ Common/modal —— **强烈建议改造**

`components/Common/modal/useCommonModal.tsx` + `index.less` + `TradeDetailModal.tsx`

**现状**：`.common-table-header`、`.modal-info-row` 等大量结构 class，且含 `[data-theme='dark']` dark 分支。

**可改造点**：

| less class | 改造方式 |
|-----------|---------|
| `.common-table-header`（bg/border-radius/padding） | 改用 antd `Card`/`div` + 内联 style，bg 用 `token.colorFillQuaternary`，去掉 dark 分支（token 自动切换） |
| `.modal-info-row`（padding-top + border-top + `.ant-space` gap） | `Divider` 组件 `styles={{ root:{...} }}`，或 `Space` + 内联；dark 的 `border-top-color` 分支删除（token 化） |
| `.common-empty-data` | 直接用 antd `<Empty>` 组件，**彻底删除**自绘 |
| `.table-group-divider` | `<Divider>` 或 `style={{ height: 24 }}` |
| `.stock-header-wrapper` / `.stock-header-left` / `.trade-count` / `.stock-header-space` | 这是**业务布局**（flex 两端对齐），需保留少量布局类，但颜色类可内联 token |

**收益**：删除 dark 分支（`[data-theme='dark'] &`）×2 处，主题切换更干净；`.common-empty-data` 改 `<Empty>` 减少自定义代码。

**预估工作量**：中。布局类（stock-header-wrapper）保留，颜色/分隔线类迁移。

---

### 3.3 ✅ CostList（Transaction） —— **建议改造（颜色部分）**

`pages/Transaction/components/CostList.tsx` + `index.less`

**现状**：BEM 命名丰富（`year-card`/`month-card`/`metric-card` 及 `__value`/`__label`/`--clickable`/`--zero`），且 tsx 里**已经几乎全部颜色用内联 `style={{ color: token.xxx }}`**，less 主要只剩布局/尺寸/响应式。

**可改造点**：

| less 内容 | 改造方式 |
|----------|---------|
| `.metric-card--clickable .metric-card__value { color: @primary-color }` | 已在 tsx 内联 `valueColor = token.colorPrimary`，**less 规则可删** |
| `.metric-card--zero .metric-card__value { color: var(--ant-color-text-tertiary) }` | 已在 tsx 内联，**可删** |
| `.metric-card--clickable:hover { background }` | `:hover` **无法**用 `styles` 表达 → 保留 less 或改 `onMouseEnter` JS（不推荐，保留 less） |
| `.year-card { border/padding/border-radius }` + `border-color` 内联 | 可考虑包一层 antd `Card`，用 `styles={{ body:{...} }}`，但 `border` 样式简单，收益有限 |
| `.metric-row` / `.month-row` flex 布局 | 纯布局，**保留 less**（`styles` 不擅长 flex 容器） |
| `@media (max-width)` 移动端 7 个指标换行 | **保留 less**（`styles` 无法表达媒体查询） |

**结论**：CostList 的 less **大部分需保留**（响应式 + flex 布局 + `:hover`），仅可清理掉**已被内联 style 顶替的冗余颜色规则**（约 2-3 条）。收益小，优先级低。

---

### 3.4 ⚠️ OverallBoard（StockList） —— **部分改造**

`pages/StockList/components/OverallBoard.tsx` + `index.less`

**现状**：`Statistic styles`、`Divider styles` 已在用；less 剩 `.expand-divider-wrapper` 的 hover 动效（用 CSS 变量 + `:hover`）。

**可改造点**：

| less 内容 | 改造方式 |
|----------|---------|
| `.expand-divider` 的 `border-block-start-color` + `.ant-divider-rail` 继承 + transition | 这是 Divider 内部结构穿透 + hover，**无法用 `styles` 表达**，保留 less |
| `.expand-icon` 的 `color` + transition + hover 变色 | `:hover` 无法用 styles，**保留** |

**结论**：OverallBoard 的 less **不建议改造**，已是最优解（CSS 变量 + React 重渲染注入，注释也说明了为何不用 `var(--ant-*)`）。

---

### 3.5 ⚠️ HoldingsList / AnalysisList —— **不建议改造表格本身**

`pages/StockList/components/HoldingsList.tsx`、`pages/ProfitAnalysis/components/AnalysisList.tsx`

**现状**：

- `.holdings-list-wrapper` 含 `overflow-x:auto` + `:global(.ant-table-thead)` sticky 表头 → **保留 less**
- `.analysis-list-wrapper` 全是移动端 `nth-child` 列宽 → `:global` 穿透，**保留 less**
- `.cell-number`（全局 class，`global.less` 定义）→ 全局工具类，**保留**
- `.table-list-wrapper` / `.table-list-header`（Common 共用）→ 布局类，**保留**

**结论**：这两个列表的容器 less 都是「布局 + 表格穿透 + 响应式」，不属于 `styles` 适用范围，**不动**。

---

### 3.6 ⚠️ RightContent —— **部分改造**

`components/RightContent/index.tsx` + `index.less`

**现状**：`.right`（flex）、`.action`（hover bg）、`.dark`（dark 分支）、` :global(.ant-pro-global-header...)`。

**可改造点**：

| less 内容 | 改造方式 |
|----------|---------|
| `.action:hover` bg | `:hover` 无法 styles → 但可考虑用 antd `Button type="text"` 替代自绘 `.action`，靠组件自带 hover |
| `.dark` avatar bg 分支 | 若改用 token（`token.colorFillSecondary`）内联，可删 dark 分支 |
| `:global(.ant-pro-global-header...)` overflow | ProLayout 内部穿透，**保留** |
| `.right` flex 布局 | 已是 `<Space>`，可大量内联 |

**结论**：优先级低。核心难点是 ProLayout 头部 `:global` 穿透，less 必须保留；`.action` 若重构成 `Button type="text"` 可减少自定义，但属交互重构，超出「样式迁移」范畴。

---

### 3.7 🚫 Login —— **不建议改造**

`pages/Login/index.tsx` + `index.less`

**现状**：品牌区（`brandPanel`/`brandTitle`/`brandDesc`/`brandSlogan`）是纯展示文案 + 渐变背景 + `@media` 双栏转单栏。

**结论**：

- 渐变背景、双栏响应式布局是**页面级布局**，不属于任何单一 antd 组件 slot，**保留 less**。
- `loginCard` 的 `border-radius !important + box-shadow` 可改 `Card styles={{ root:{...} }}`，但收益极小。
- `.submit-button`（width:100%）可改 `ProForm submitter` 的 `submitButtonProps={{ block:true }}`，**这个值得做**（1 行改动，删 1 条 less）。

**仅建议**：`submitButton` 改 `block` 属性；其余保留。

---

### 3.8 🚫 global.less / variables.less —— **不动**

- `global.less`：reset、ProLayout 背景、移动端全局表格/Modal 适配 —— 全是 `:global` 与全局选择器，`styles` 无法替代。
- `variables.less`：构建期注入的 less 变量，删除会破坏 `@primary-color` 等引用。

---

## 四、改造优先级排序

| 优先级 | 目标 | 改造动作 | 收益 | 风险 | 工作量 |
|--------|------|---------|------|------|--------|
| **P0** | `Account` 页面 | 自绘键值表 → `Descriptions`；删除 `Account/index.less` | 删 1 个 less 文件，代码更声明式 | 低 | 小（0.5h） |
| **P0** | `Common/modal` 颜色/dark 分支 | `.common-table-header`/`.modal-info-row` 颜色改内联 token，删 dark 分支；`.common-empty-data` → `<Empty>` | 删 dark 分支 ×2，主题更干净 | 低 | 小（1h） |
| **P1** | `Login` 提交按钮 | `.submit-button` → `submitButtonProps={{ block:true }}` | 删 1 条 less | 极低 | 极小（5min） |
| **P2** | `CostList` 冗余颜色规则 | 删除已被内联 style 顶替的 `metric-card--clickable`/`--zero` 颜色规则 | 清理死代码 | 极低 | 小（15min） |
| **P3** | `RightContent` dark 分支 | avatar/action 颜色改 token 内联，删 `.dark` 分支 | 减少分支 | 低 | 小 |
| **—** | `OverallBoard`/`HoldingsList`/`AnalysisList`/`global.less`/`variables.less` | **不改造** | — | — | — |

---

## 五、改造示例（仅 P0，供评审）

### 5.1 Account —— 自绘键值表 → Descriptions

**改造前**（`index.tsx` + 8 个 less class）

```tsx
<Card className={styles.card} styles={{ body: { padding: 24 } }}>
  <div className={styles.header}>
    <Avatar size={64} icon={<UserOutlined />} className={styles.avatar} />
    <div>
      <div className={styles.name}>{user?.name}</div>
      <div className={styles.username}>{user?.username}</div>
    </div>
  </div>
  <div className={styles.table}>
    {rows.map(([label, value]) => (
      <div key={label} className={styles.row}>
        <div className={styles.label}>{label}</div>
        <div className={styles.value}>{value}</div>
      </div>
    ))}
  </div>
</Card>
```

**改造后**（无 less，纯组件 + token）

```tsx
const { token } = theme.useToken();

<Card
  variant="bordered"
  style={{ maxWidth: 480, margin: '0 auto', borderColor: token.colorBorderSecondary }}
  styles={{ body: { padding: 24 } }}
>
  <Space size={16} style={{ marginBottom: 24 }}>
    <Avatar size={64} icon={<UserOutlined />} style={{ backgroundColor: token.colorPrimary }} />
    <Space direction="vertical" size={0}>
      <Typography.Title level={4} style={{ margin: 0 }}>{user?.name}</Typography.Title>
      <Typography.Text type="secondary">{user?.username}</Typography.Text>
    </Space>
  </Space>
  <Descriptions
    column={1}
    size="small"
    bordered
    styles={{
      label: { width: 100, background: token.colorFillQuaternary },
      content: { color: token.colorText },
    }}
    items={[
      { key: 'username', label: '用户名', children: user?.username },
      { key: 'name', label: '显示名称', children: user?.name },
      { key: 'role', label: '角色', children: <Tag style={meta.tag(token)}>{meta.label}</Tag> },
    ]}
  />
</Card>
```

> `Account/index.less` 可整文件删除。

### 5.2 Common/modal —— 颜色 token 化 + `<Empty>`

**改造前**（`modal/index.less` 含 dark 分支）

```less
.modal-info-row-base() {
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  [data-theme='dark'] & { border-top-color: rgba(255, 255, 255, 0.1); }
}
.common-table-header {
  background-color: rgba(0, 0, 0, 0.02);
  [data-theme='dark'] & { background-color: rgba(255, 255, 255, 0.04); }
}
```

**改造后**（tsx 内联 token，dark 自动切换，删 less 分支）

```tsx
const { token } = theme.useToken();

// 表头
<div style={{ padding: '8px 12px', background: token.colorFillQuaternary, borderRadius: 4, marginBottom: 12 }}>
  {headerView}
</div>

// 分隔行
<div style={{ paddingTop: 8, borderTop: `1px solid ${token.colorBorderSecondary}` }}>
  <Space size={8} wrap>{infoItems}</Space>
</div>

// 空数据 → 直接用组件
<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />
```

---

## 六、不建议用 `styles` 的场景（明确边界）

为避免误改造，以下场景 **必须保留 less**：

1. **伪类**：`:hover`、`&:last-child`、`:nth-child(n)` → `styles` 不支持伪类。
2. **媒体查询**：`@media (max-width: @screen-md)` → `styles` 不支持，需 less 或 CSS-in-JS（项目未用 emotion/styled）。
3. **穿透子组件**：`:global(.ant-table-thead > tr > th)`、`:global(.ant-pro-global-header)` → 只能 less。
4. **全局 reset / 构建期变量**：`global.less`、`variables.less`。
5. **页面级/多元素布局**：flex 容器、双栏响应式（如 Login 品牌区）→ 不属于单一组件 slot。
6. **动画/transition**：`OverallBoard` 的 divider hover 过渡 → 保留 less + CSS 变量方案。

---

## 七、落地建议

1. **分批 PR**：按 P0 → P1 → P2 顺序，每批独立可回滚。
2. **验证方式**：每批改完跑 `ut run type-check` + 手动验证对应页面（明暗主题切换）。
3. **删除 less 前确认**：grep 该 class 是否被其它页面引用（如 `.table-list-header` 被 CostList/AnalysisList 共用，不可随单页删除）。
4. **Docker 提醒**：改前端后须 `docker compose build frontend && docker compose up -d frontend` 才生效。

---

## 附：antd 6 常用组件 `styles` slot 速查

| 组件 | 可用 slot |
|------|----------|
| `Card` | `header`, `body`, `actions`, `extra` |
| `Modal`/`modal.info` | `header`, `body`, `footer`, `content`, `mask`, `wrapper` |
| `Table` | `header`, `body`, `content`, `table`（含 `header.cell`/`body.cell`/`body.row` 等） |
| `Statistic` | `title`, `content`, `value` |
| `Divider` | `root`, `content` |
| `Tooltip` | `root`, `inner`, `container`, `arrow` |
| `Descriptions` | `header`, `body`, `label`, `content`, `view` |
| `Tag` | 无 `styles`，用 `style` |
| `Drawer` | `header`, `body`, `footer`, `content`, `wrapper`, `mask` |

> 完整 slot 以 antd 6 文档与 TS 类型提示为准。
