import React from 'react';
import { ProCard } from '@ant-design/pro-components';
import { useStocks } from '@/hooks/useStocks';
import { AnalysisList } from './components/AnalysisList';
import '@/components/Common/index.less';

const ProfitAnalysisPage: React.FC = () => {
  const { stock, loading } = useStocks();

  return (
    <div className="page-container">
      <ProCard>
        <AnalysisList data={stock} loading={loading} />
      </ProCard>
    </div>
  );
};

export default ProfitAnalysisPage;
