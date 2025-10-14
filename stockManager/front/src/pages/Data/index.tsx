import React from 'react';
import ProCard from '@ant-design/pro-card';

import { Tabs, Statistic, Row, Col } from 'antd';
import { useModel } from 'umi';

const { TabPane } = Tabs;

import { AnalysisList } from '../../components/Table/AnalysisList';
import { CostList } from '../../components/Table/CostList';

export default (): React.ReactNode => {
  const { stock } = useModel('stocks');

  return (
    <ProCard gutter={[0, 16]}>
      <Tabs defaultActiveKey="1">
        <TabPane tab="盈亏归因" key="1">
          <AnalysisList data={stock.stocks} incomeCash={stock.overall.incomeCash} />
        </TabPane>
        <TabPane tab="费用明细" key="2">
          <Row>
            <Statistic title="总费用" value={stock.overall.totalCost.toFixed(2)} />
          </Row>
          <Row style={{ marginTop: '20px' }}>
            <Col span={24}>
              <CostList data={stock.stocks} />
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </ProCard>
  );
};
