import { Table, Button, Tabs, Row, Col } from 'antd';
const { TabPane } = Tabs;
import React, { useState, useEffect } from 'react';

import ProCard from '@ant-design/pro-card';

import { history } from 'umi';
import { fetch } from '../../services/api';

import { Columns, ColumnsOverAll, ColumnsOperation } from '../../types/tableList';

import './index.less';

const TableList: React.FC = () => {
  const [overAllData, setOverallData] = useState({} as API.Overall);
  const [stockData, setStockData] = useState([] as API.Stock[]);

  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const response = await fetch();
    if (response.status == 1 && !!response.data) {
      setOverallData(response.data?.overall);
      setStockData(response.data?.stocks);
    } else {
      history.push('/login');
    }
  };

  const rowClassName = (record: API.Stock, index: number): string => {
    return record.totalValue < 0.1 && !showAll ? 'hide' : '';
  };

  const expandedRowRender = (record: API.Stock) => {
    return (
      <Table
        style={{ marginTop: '10px', marginBottom: '10px' }}
        columns={ColumnsOperation}
        size="small"
        bordered
        tableLayout="fixed"
        dataSource={record.operationList}
        pagination={false}
      ></Table>
    );
  };

  return (
    <ProCard direction="column" ghost gutter={[0, 8]}>
      <ProCard colSpan={24}>
        <Table columns={ColumnsOverAll} dataSource={[overAllData]} bordered pagination={false} />
      </ProCard>
      <ProCard colSpan={24}>
        <Row>
          <Col offset={20} span={6}>
            <Button type="primary" onClick={() => setShowAll(!showAll)}>
              {(showAll ? '隐藏' : '显示') + '市值为零的股票'}
            </Button>
          </Col>
        </Row>
        <Row style={{ marginTop: '20px' }}>
          <Col span={24}>
            <Table
              rowKey="code"
              columns={Columns}
              dataSource={stockData}
              bordered
              pagination={false}
              rowClassName={rowClassName}
              expandable={{ expandedRowRender }}
            />
          </Col>
        </Row>
      </ProCard>
    </ProCard>
  );
};

export default TableList;
