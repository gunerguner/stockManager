import React from 'react';
import { ProCard } from '@ant-design/pro-components';
import { theme } from 'antd';
import { useStocks } from '@/hooks/useStocks';
import { AnalysisList } from './components/AnalysisList';
import '@/components/Common/index.less';

const ProfitAnalysisPage: React.FC = () => {
  const { stock, loading } = useStocks();
  const { token } = theme.useToken();

  return (
    <div className="page-container">
      <ProCard
        styles={{
          root: {
            background: token.colorBgContainer,
            borderColor: token.colorBorderSecondary,
          },
        }}
      >
        <AnalysisList data={stock} loading={loading} />
      </ProCard>
    </div>
  );
};

export default ProfitAnalysisPage;
