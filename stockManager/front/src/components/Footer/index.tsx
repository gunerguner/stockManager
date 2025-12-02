import React from 'react';
import { GithubOutlined, AntDesignOutlined } from '@ant-design/icons';
import { DefaultFooter } from '@ant-design/pro-layout';

const START_YEAR = 2020;
const CURRENT_YEAR = new Date().getFullYear();
const COPYRIGHT = `${START_YEAR}${CURRENT_YEAR > START_YEAR ? `-${CURRENT_YEAR}` : ''} 溯宁`;

const FOOTER_LINKS = [
  { key: 'umijs', title: 'UmiJS', href: 'https://umijs.org', blankTarget: true },
  { key: 'ant-design', title: <AntDesignOutlined />, href: 'https://ant.design', blankTarget: true },
  { key: 'github', title: <GithubOutlined />, href: 'https://github.com/gunerguner/stockManager', blankTarget: true },
  { key: 'icp', title: '沪ICP备2020026170号', href: 'https://beian.miit.gov.cn/', blankTarget: true },
];

const Footer: React.FC = () => <DefaultFooter copyright={COPYRIGHT} links={FOOTER_LINKS} />;

export default Footer;
