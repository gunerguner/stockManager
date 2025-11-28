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
      <Tabs defaultActiveKey="1">
        <Tabs.TabPane tab="盈亏归因" key="1">
          <AnalysisList data={stock.stocks} incomeCash={stock.overall.incomeCash} />
        </Tabs.TabPane>
        <Tabs.TabPane tab="费用明细" key="2">
          <CostList data={stock.stocks} totalCost={stock.overall.totalCost} />
        </Tabs.TabPane>
      </Tabs>
    </ProCard>
  );
};

export default DataPage;
