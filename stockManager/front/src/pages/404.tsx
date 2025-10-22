import { Button, Result } from 'antd';
import { HomeOutlined, RollbackOutlined } from '@ant-design/icons';
import React from 'react';
import { history } from 'umi';

const NoFoundPage: React.FC = () => {
  const handleGoHome = (): void => {
    history.push('/');
  };

  const handleGoBack = (): void => {
    history.goBack();
  };

  return (
    <Result
      status="404"
      title="404"
      subTitle="抱歉，您访问的页面不存在"
      extra={[
        <Button type="primary" icon={<HomeOutlined />} onClick={handleGoHome} key="home">
          返回首页
        </Button>,
        <Button icon={<RollbackOutlined />} onClick={handleGoBack} key="back">
          返回上一页
        </Button>,
      ]}
    />
  );
};

export default NoFoundPage;
