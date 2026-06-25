import React from 'react';
import { ProCard } from '@ant-design/pro-components';
import { useStocks } from '@/hooks/useStocks';
import { CostList } from './components/CostList';

const TransactionPage: React.FC = () => {
  const { stock, operations, loading } = useStocks();

  return (
    <div style={{ borderRadius: 8, padding: 16 }}>
      <ProCard>
        <CostList data={stock} operations={operations} loading={loading} />
      </ProCard>
    </div>
  );
};

export default TransactionPage;
