export default [
  {
    path: '/user',
    layout: false,
    routes: [
      {
        path: '/user',
        routes: [
          {
            name: 'login',
            path: '/user/login',
            component: './user/Login',
          },
        ],
      },
    ],
  },
  {
    name: '持仓盈亏',
    icon: 'table',
    path: '/list',
    component: './TableList',
  },
  {
    path: '/data',
    name: '数据分析',
    icon: 'database',
    component: './Data',
  },
  {
    path: '/admin',
    name: '后台管理',
    icon: 'crown',
    access: 'canAdmin',
    component: './Admin',
    
  },
  {
    path: '/',
    redirect: '/TableList',
  },
  {
    component: './404',
  },
];
