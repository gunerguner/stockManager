import { useEffect, useState } from 'react';
import { App, Radio, Space, Typography, theme } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import type { NavRefreshSpan } from '@/services/api';
import { NavContent } from './components/NavContent';
import { NavToolbar } from './components/NavToolbar';
import type { NavRangeKey } from './components/navStat';
import '@/components/Common/index.less';

const RANGE_REFRESH_OPTIONS: { value: NavRefreshSpan; label: string }[] = [
  { value: 'week', label: '近一周' },
  { value: 'month', label: '近一月' },
  { value: 'quarter', label: '近三月' },
];

const RangeRefreshFields: React.FC<{
  onSpanChange: (span: NavRefreshSpan) => void;
}> = ({ onSpanChange }) => (
  <Space orientation="vertical">
    <Typography.Text>
      将重算所选区间内的净值。更早的交易或出入金仍需全量刷新。
    </Typography.Text>
    <Radio.Group
      defaultValue="month"
      options={RANGE_REFRESH_OPTIONS}
      onChange={(event) => onSpanChange(event.target.value as NavRefreshSpan)}
    />
  </Space>
);

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
          onRangeRefresh={() => {
            let span: NavRefreshSpan = 'month';
            modal.confirm({
              title: '区间刷新净值',
              content: (
                <RangeRefreshFields
                  onSpanChange={(next) => {
                    span = next;
                  }}
                />
              ),
              okText: '刷新',
              cancelText: '取消',
              onOk: () => refreshNavData('recent', span),
            });
          }}
          onFullRefresh={() => {
            modal.confirm({
              title: '确定全量刷新净值？',
              content:
                '将从头重算全部交易日净值，耗时更长。近一周、近一月、近三月内的修改可用「区间刷新」；更早的历史交易或出入金请使用此项。',
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
