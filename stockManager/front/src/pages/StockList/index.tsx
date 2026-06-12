import { FloatButton } from 'antd';
import { useState } from 'react';
import { ProCard } from '@ant-design/pro-components';
import { OverallBoard } from './components/OverallBoard';
import { OperationList } from './components/OperationList';
import { FilterPanel } from './components/FilterPanel';
import { useStocks } from '@/hooks/useStocks';

const StockList: React.FC = () => {
  const [showAll, setShowAll] = useState(false);
  const [showConv, setShowConv] = useState(true);
  const { stock, operations, fetchStockData, loading } = useStocks();

  return (
    <>
      <FloatButton.BackTop />
      <div style={{ borderRadius: 8, padding: 16 }}>
        <ProCard>
          <OverallBoard data={stock.overall} onModifySuccess={fetchStockData} />
          <FilterPanel
            showAll={showAll}
            showConv={showConv}
            onRefresh={fetchStockData}
            onShowAllChange={setShowAll}
            onShowConvChange={setShowConv}
          />
          <OperationList
            showAll={showAll}
            showConv={showConv}
            data={stock}
            operations={operations}
            loading={loading}
          />
        </ProCard>
      </div>
    </>
  );
};

export default StockList;
