import { Button, Row, Col } from 'antd';

import React, { useState, useEffect } from 'react';

import ProCard from '@ant-design/pro-card';

import { history, useModel } from 'umi';
import { fetch } from '../../services/api';
import { ReloadOutlined } from '@ant-design/icons';

import { OverallBoard } from '../../components/Table/OverallBoard';
import { OperationList } from '../../components/Table/OperationList';

import './index.less';

const TableList: React.FC = () => {
  const [showAll, setShowAll] = useState(false);
  const { stock, setStockData } = useModel('stocks');

  useEffect(() => {
    fetchData();
  }, []);

  
  const fetchData = async () => {
    const response = await fetch();
    if (response.status == 1 && !!response.data) {
      setStockData(response.data);
    } else if (response.status == 302) {
      history.push('/login');
    }
  };

  const overallModifyCompeletion = (type: string, success: boolean) => {
    success ? fetchData() : history.push('/login');
  };

  return (
    <ProCard direction="column" ghost gutter={[0, 8]}>
      <ProCard colSpan={24}>
        <OverallBoard data={stock.overall} compeletion={overallModifyCompeletion} />
      </ProCard>
      <ProCard colSpan={24}>
        <Row>
          <Col span={2} offset={18}>
            <Button onClick={fetchData} icon={<ReloadOutlined />} />
          </Col>
          <Col span={4}>
            <Button type="primary" onClick={() => setShowAll(!showAll)}>
              {(showAll ? '隐藏' : '显示') + '市值为零的股票'}
            </Button>
          </Col>
        </Row>
        <Row style={{ marginTop: '20px' }}>
          <Col span={24}>
            <OperationList showAll={showAll} data={stock} />
          </Col>
        </Row>
      </ProCard>
    </ProCard>
  );
};

export default TableList;
