import { FloatButton } from 'antd';
import React, { useState, useCallback } from 'react';
import ProCard from '@ant-design/pro-card';
import { OverallBoard } from '@/components/Table/OverallBoard';
import { OperationList } from '@/components/Table/OperationList';
import { FilterPanel } from '@/components/Table/FilterPanel';
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
      <div className="table-list-container">
        {/* 整体数据面板 */}
        <ProCard>
          <OverallBoard data={stock.overall} completion={handleOverallModifyCompletion} />
        </ProCard>

        {/* 筛选控制面板 */}
        <ProCard>
          <FilterPanel
            showAll={showAll}
            showConv={showConv}
            onRefresh={fetchStockData}
            onShowAllChange={handleShowAllChange}
            onShowConvChange={handleShowConvChange}
          />
        </ProCard>

        {/* 操作列表面板 */}
        <ProCard>
          <OperationList showAll={showAll} showConv={showConv} data={stock} />
        </ProCard>
      </div>
    </>
  );
};

export default TableList;
