import React from 'react';
import { ProCard } from '@ant-design/pro-components';
import { useStocks } from '@/hooks/useStocks';
import { CostList } from './components/CostList';
import '@/components/Common/index.less';

const TransactionPage: React.FC = () => {
  const { stock, operations, loading } = useStocks();

  return (
    <div className="page-container">
      <ProCard>
        <CostList data={stock} operations={operations} loading={loading} />
      </ProCard>
    </div>
  );
};

export default TransactionPage;
