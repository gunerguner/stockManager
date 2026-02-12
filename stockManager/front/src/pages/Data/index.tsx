import React from 'react';
import { Tabs } from 'antd';
import ProCard from '@ant-design/pro-card';
import { useStocks } from '@/hooks/useStocks';

import { AnalysisList } from './components/AnalysisList';
import { CostList } from './components/CostList';

const DataPage: React.FC = () => {
  const { stock } = useStocks();

  return (
    <ProCard gutter={[0, 16]}>
      <Tabs
        defaultActiveKey="1"
        items={[
          {
            key: '1',
            label: '盈亏归因',
            children: <AnalysisList data={stock.stocks} incomeCash={stock.overall.incomeCash} />,
          },
          {
            key: '2',
            label: '费用明细',
            children: <CostList data={stock.stocks} totalCost={stock.overall.totalCost} />,
          },
        ]}
      />
    </ProCard>
  );
};

export default DataPage;
