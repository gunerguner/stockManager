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
    path: '/data',
    name: '数据分析',
    icon: 'database',
    component: './Data',
  },
  {
    path: '/watch',
    name: '关注列表',
    icon: 'star',
    component: './Watch',
  },
  {
    path: '/admin',
    name: '后台管理',
    icon: 'crown',
    access: 'canAdmin',
    component: './Admin',
    
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
