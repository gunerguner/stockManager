import { Button, Row, Col, Checkbox, BackTop } from 'antd';
import React, { useState, useEffect, useCallback } from 'react';
import ProCard from '@ant-design/pro-card';
import { history, useModel } from 'umi';
import { ReloadOutlined } from '@ant-design/icons';

import { fetch } from '../../services/api';
import { OverallBoard } from '../../components/Table/OverallBoard';
import { OperationList } from '../../components/Table/OperationList';

import './index.less';

const TableList: React.FC = () => {
  const [showAll, setShowAll] = useState(false);
  const [showConv, setShowConv] = useState(true);
  const { stock, setStockData } = useModel('stocks');

  const fetchData = useCallback(async () => {
    const response = await fetch();
    if (response.status === 1 && !!response.data) {
      setStockData(response.data);
    } else if (response.status === 302) {
      history.push('/login');
    }
  }, [setStockData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const overallModifyCompeletion = useCallback(
    (type: string, success: boolean) => {
      if (success) {
        fetchData();
      } else {
        history.push('/login');
      }
    },
    [fetchData],
  );

  return (
    <>
      <BackTop />
      <ProCard direction="column" ghost gutter={[0, 8]}>
        <ProCard colSpan={24}>
          <OverallBoard data={stock.overall} compeletion={overallModifyCompeletion} />
        </ProCard>
        <ProCard colSpan={24}>
          <Row align="middle">
            <Col span={2}>
              <Button onClick={fetchData} icon={<ReloadOutlined />} />
            </Col>
            <Col span={4} offset={15}>
              <Checkbox checked={showAll} onChange={(e) => setShowAll(e.target.checked)}>
                显示市值为零的股票
              </Checkbox>
            </Col>
            <Col span={3}>
              <Checkbox checked={showConv} onChange={(e) => setShowConv(e.target.checked)}>
                显示可转债
              </Checkbox>
            </Col>
          </Row>
          <Row style={{ marginTop: '20px' }}>
            <Col span={24}>
              <OperationList showAll={showAll} showConv={showConv} data={stock} />
            </Col>
          </Row>
        </ProCard>
      </ProCard>
    </>
  );
};

export default TableList;
