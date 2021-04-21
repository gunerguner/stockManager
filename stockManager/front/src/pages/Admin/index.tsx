import React from 'react';

import { Alert, Button } from 'antd';

import ProCard from '@ant-design/pro-card';

export default (): React.ReactNode => {
  return (

      <ProCard  gutter={[0, 16]}>
        <Button type = 'primary'
          style={{
            margin: 8,
          }}
        >
          更新除权信息
        </Button>
      </ProCard>

  );
};
