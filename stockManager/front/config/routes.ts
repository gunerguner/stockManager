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
    path: '/data',
    name: '数据分析',
    icon: 'database',
    component: './Data',
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
