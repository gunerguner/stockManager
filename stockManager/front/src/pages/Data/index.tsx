import React from 'react';
import { Tabs } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useStocks } from '@/hooks/useStocks';

import { AnalysisList } from './components/AnalysisList';
import { CostList } from './components/CostList';

const DataPage: React.FC = () => {
  const { stock, operations, loading } = useStocks();

  return (
    <div style={{ borderRadius: 8, padding: 16 }}>
      <ProCard gutter={[0, 16]}>
        <Tabs
          defaultActiveKey="1"
          items={[
            {
              key: '1',
              label: '盈亏归因',
              children: <AnalysisList data={stock} loading={loading} />,
            },
            {
              key: '2',
              label: '费用明细',
              children: <CostList data={stock} operations={operations} loading={loading} />,
            },
          ]}
        />
      </ProCard>
    </div>
  );
};

export default DataPage;
