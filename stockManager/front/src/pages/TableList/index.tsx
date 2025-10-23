import { Button, Row, Col, Checkbox, FloatButton } from 'antd';
import React, { useState, useEffect, useCallback } from 'react';
import { ProCard } from '@ant-design/pro-components';
import { history, useModel } from '@umijs/max';
import { ReloadOutlined } from '@ant-design/icons';
import { getStockList } from '@/services/api';
import { OverallBoard } from '@/components/Table/OverallBoard';
import { OperationList } from '@/components/Table/OperationList';
import './index.less';

const TableList: React.FC = () => {
  // 筛选条件状态
  const [showAll, setShowAll] = useState<boolean>(false);
  const [showConv, setShowConv] = useState<boolean>(true);
  const { stock, setStockData } = useModel('stocks');

  /**
   * 获取股票列表数据
   */
  const fetchData = useCallback(async (): Promise<void> => {
    const response = await getStockList();

    if (response.status === 1 && response.data) {
      setStockData(response.data);
    } else if (response.status === 302) {
      history.push('/login');
    }
  }, [setStockData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  /**
   * 整体数据修改完成回调
   * @param success - 操作是否成功
   */
  const handleOverallModifyCompletion = useCallback(
    (success: boolean): void => {
      if (success) {
        fetchData();
      } else {
        history.push('/login');
      }
    },
    [fetchData],
  );

  const handleShowAllChange = (checked: boolean): void => {
    setShowAll(checked);
  };

  const handleShowConvChange = (checked: boolean): void => {
    setShowConv(checked);
  };

  return (
    <>
      <FloatButton.BackTop />
      <ProCard direction="column" ghost gutter={[0, 8]}>
        {/* 整体数据面板 */}
        <ProCard colSpan={24}>
          <OverallBoard data={stock.overall} completion={handleOverallModifyCompletion} />
        </ProCard>

        {/* 操作列表面板 */}
        <ProCard colSpan={24}>
          <Row align="middle" gutter={[16, 16]}>
            <Col xs={24} sm={4} md={2}>
              <Button onClick={fetchData} icon={<ReloadOutlined />} block>
                刷新
              </Button>
            </Col>
            <Col xs={24} sm={10} md={4} offset={0} lg={{ offset: 15 }}>
              <Checkbox checked={showAll} onChange={(e) => handleShowAllChange(e.target.checked)}>
                显示市值为零的股票
              </Checkbox>
            </Col>
            <Col xs={24} sm={10} md={3}>
              <Checkbox
                checked={showConv}
                onChange={(e) => handleShowConvChange(e.target.checked)}
              >
                显示可转债
              </Checkbox>
            </Col>
          </Row>

          <Row className="operation-list-row">
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
