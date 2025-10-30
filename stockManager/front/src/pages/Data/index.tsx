import React, { useMemo } from 'react';
import { Tabs, Statistic, Row, Col } from 'antd';
import ProCard from '@ant-design/pro-card';
import { useModel } from '@umijs/max';

import { AnalysisList } from '../../components/Table/AnalysisList';
import { CostList } from '../../components/Table/CostList';
import styles from './index.less';


const DataPage: React.FC = () => {
  const { stock } = useModel('stocks');

  // 格式化总费用，避免运行时错误
  const formattedTotalCost = useMemo(() => {
    const totalCost = stock?.overall?.totalCost ?? 0;
    return totalCost.toFixed(2);
  }, [stock?.overall?.totalCost]);

  // 安全获取数据
  const stocksData = stock?.stocks ?? [];
  const incomeCash = stock?.overall?.incomeCash ?? 0;

  return (
    <ProCard gutter={[0, 16]}>
      <Tabs defaultActiveKey="1">
        <Tabs.TabPane tab="盈亏归因" key="1">
          <AnalysisList data={stocksData} incomeCash={incomeCash} />
        </Tabs.TabPane>
        <Tabs.TabPane tab="费用明细" key="2">
          <Row>
            <Statistic title="总费用" value={formattedTotalCost} />
          </Row>
          <Row className={styles.costRow}>
            <Col span={24}>
              <CostList data={stocksData} />
            </Col>
          </Row>
        </Tabs.TabPane>
      </Tabs>
    </ProCard>
  );
};

export default DataPage;
