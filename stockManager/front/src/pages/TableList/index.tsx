import { Button, Row, Col, Checkbox, FloatButton } from 'antd';
import React, { useState, useCallback } from 'react';
import ProCard from '@ant-design/pro-card';
import { ReloadOutlined } from '@ant-design/icons';
import { OverallBoard } from '@/components/Table/OverallBoard';
import { OperationList } from '@/components/Table/OperationList';
import { useStocks } from '@/hooks/useStocks';
import './index.less';

const TableList: React.FC = () => {
  // 筛选条件状态
  const [showAll, setShowAll] = useState<boolean>(false);
  const [showConv, setShowConv] = useState<boolean>(true);
  
  // 使用自定义 Hook 自动加载股票数据
  const { stock, fetchStockData } = useStocks();

  /**
   * 整体数据修改完成回调
   * @param success - 操作是否成功
   */
  const handleOverallModifyCompletion = useCallback(
    (success: boolean): void => {
      if (success) {
        fetchStockData();
      }
      // 失败情况在 fetchStockData 中已处理（跳转登录）
    },
    [fetchStockData],
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
        {stock.overall && (
          <ProCard colSpan={24}>
            <OverallBoard data={stock.overall} completion={handleOverallModifyCompletion} />
          </ProCard>
        )}

        {/* 操作列表面板 */}
        <ProCard colSpan={24}>
          <Row align="middle" gutter={[16, 16]}>
            <Col xs={24} sm={4} md={2}>
              <Button onClick={fetchStockData} icon={<ReloadOutlined />} block>
                刷新
              </Button>
            </Col>
            <Col xs={12} sm={10} md={4} offset={0} lg={{ offset: 15 }}>
              <Checkbox checked={showAll} onChange={(e) => handleShowAllChange(e.target.checked)}>
                显示市值为零的股票
              </Checkbox>
            </Col>
            <Col xs={12} sm={10} md={3}>
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
