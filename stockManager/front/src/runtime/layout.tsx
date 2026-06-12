import React from 'react';
import type { RuntimeConfig } from '@umijs/max';
import { history, useModel } from '@umijs/max';
import RightContent from '@/components/RightContent';
import Footer from '@/components/Footer';
import ThemeLayoutSync from '@/components/ThemeLayoutSync';
import defaultSettings from '../../config/defaultSettings';
import { LOGIN_PATH } from './constants';

const DynamicLogo: React.FC = () => {
  const { actualTheme } = useModel('theme');
  const { initialState } = useModel('@@initialState');
  const settings = initialState?.settings as typeof defaultSettings;

  const logoUrl =
    actualTheme === 'dark'
      ? settings?.logoDark || settings?.logo
      : settings?.logoLight || settings?.logo;

  return <img src={logoUrl} alt="logo" style={{ height: '32px' }} />;
};

export const layout: RuntimeConfig['layout'] = ({ initialState }) => ({
  ...initialState?.settings,
  actionsRender: () => <RightContent />,
  rightContentRender: false,
  disableContentMargin: false,
  footerRender: () => <Footer />,
  onPageChange: () => {
    const { location } = history;
    if (!initialState?.currentUser && location.pathname !== LOGIN_PATH) {
      history.push(LOGIN_PATH);
    }
  },
  menuHeaderRender: undefined,
  logo: <DynamicLogo />,
  childrenRender: (children) => (
    <>
      <ThemeLayoutSync />
      {children}
    </>
  ),
});
