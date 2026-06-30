import { FloatButton } from 'antd';
import { useState } from 'react';
import { ProCard } from '@ant-design/pro-components';
import { OverallBoard } from './components/OverallBoard';
import { HoldingsList } from './components/HoldingsList';
import { StockListToolbar } from './components/StockListToolbar';
import { useStocks } from '@/hooks/useStocks';
import '@/components/Common/index.less';

const StockList: React.FC = () => {
  const [showAll, setShowAll] = useState(false);
  const [showConv, setShowConv] = useState(true);
  const { stock, operations, fetchStockData, loading } = useStocks();

  return (
    <>
      <FloatButton.BackTop />
      <div className="page-container">
        <ProCard>
          <OverallBoard data={stock.overall} onModifySuccess={fetchStockData} />
          <StockListToolbar
            showAll={showAll}
            showConv={showConv}
            onRefresh={fetchStockData}
            onShowAllChange={setShowAll}
            onShowConvChange={setShowConv}
          />
          <HoldingsList
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
