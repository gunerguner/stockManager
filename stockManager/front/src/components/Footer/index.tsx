import { GithubOutlined, AntDesignOutlined } from '@ant-design/icons';
import { DefaultFooter } from '@ant-design/pro-layout';

export default () => (
  <DefaultFooter
    copyright="2020-2022 溯宁出品"
    links={[
      {
        key: 'UmiJS',
        title: 'UmiJS',
        href: 'https://umijs.org',
        blankTarget: true,
      },
      {
        key: 'Ant Design',
        title: <AntDesignOutlined />,
        href: 'https://ant.design',
        blankTarget: true,
      },
      {
        key: 'github',
        title: <GithubOutlined />,
        href: 'https://github.com/gunerguner/stockManager',
        blankTarget: true,
      },
      {
        key: 'icp',
        title: '沪ICP备2020026170号',
        href: 'https://beian.miit.gov.cn/',
        blankTarget: true,
      },
    ]}
  />
);
