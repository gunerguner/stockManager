import React from 'react';
import { ProCard } from '@ant-design/pro-components';
import { theme } from 'antd';
import { useStocks } from '@/hooks/useStocks';
import { CostList } from './components/CostList';
import '@/components/Common/index.less';

const TransactionPage: React.FC = () => {
  const { stock, operations, loading } = useStocks();
  const { token } = theme.useToken();

  return (
    <div className="page-container">
      <ProCard
        styles={{
          root: {
            background: token.colorBgContainer,
            borderColor: token.colorBorderSecondary,
          },
        }}
      >
        <CostList data={stock} operations={operations} loading={loading} />
      </ProCard>
    </div>
  );
};

export default TransactionPage;
