export default [
   
  {
    path: '/login',
    component: './Login',
    layout: false,
  },
  {
    name: '持仓盈亏',
    icon: 'table',
    path: '/list',
    component: './StockList',
  },
  {
    path: '/watch',
    name: '关注列表',
    icon: 'star',
    component: './Watch',
  },
  {
    path: '/profit-analysis',
    name: '盈亏归因',
    icon: 'fileSearch',
    component: './ProfitAnalysis',
  },
  {
    path: '/transaction',
    name: '交易数据',
    icon: 'database',
    component: './Transaction',
  },
  {
    path: '/account',
    component: './Account',
  },
  {
    path: '/',
    redirect: '/list',
  },
  {
    component: './404',
  },
];
