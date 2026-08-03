import { useEffect, useState } from 'react';
import { App, theme } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { NavContent } from './components/NavContent';
import { NavToolbar } from './components/NavToolbar';
import type { NavRangeKey } from './components/navStat';
import '@/components/Common/index.less';

const NavAnalysisPage: React.FC = () => {
  const [range, setRange] = useState<NavRangeKey>('all');
  const { modal } = App.useApp();
  const {
    data,
    loading,
    refreshing,
    initialized,
    fetchNavAnalysis,
    refreshNavData,
  } = useModel('navAnalysis');
  const { token } = theme.useToken();

  useEffect(() => {
    if (!initialized) void fetchNavAnalysis();
  }, [initialized, fetchNavAnalysis]);

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
        <NavToolbar
          range={range}
          lastDate={data?.lastDate}
          refreshing={refreshing}
          onRangeChange={setRange}
          onIncrementalRefresh={() => void refreshNavData('incremental')}
          onFullRefresh={() => {
            modal.confirm({
              title: '确定全量刷新净值？',
              content:
                '将从头重算全部交易日净值，耗时更长。修改过历史交易/出入金时请使用此项。',
              onOk: () => refreshNavData('full'),
            });
          }}
        />
        <NavContent
          data={data}
          range={range}
          loading={loading}
          refreshing={refreshing}
        />
      </ProCard>
    </div>
  );
};

export default NavAnalysisPage;
