import React from 'react';
import { ProCard } from '@ant-design/pro-components';
import { useStocks } from '@/hooks/useStocks';
import { AnalysisList } from './components/AnalysisList';

const ProfitAnalysisPage: React.FC = () => {
  const { stock, loading } = useStocks();

  return (
    <div style={{ borderRadius: 8, padding: 16 }}>
      <ProCard>
        <AnalysisList data={stock} loading={loading} />
      </ProCard>
    </div>
  );
};

export default ProfitAnalysisPage;
