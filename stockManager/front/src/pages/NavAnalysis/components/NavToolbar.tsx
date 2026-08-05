import { Button, Segmented, Space, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useIsMobile } from '@/hooks/useIsMobile';
import { NAV_RANGE_OPTIONS, type NavRangeKey } from './navStat';
import './index.less';

type NavToolbarProps = {
  range: NavRangeKey;
  lastDate?: string | null;
  refreshing?: boolean;
  onRangeChange: (range: NavRangeKey) => void;
  onIncrementalRefresh: () => void;
  onFullRefresh: () => void;
};

export const NavToolbar: React.FC<NavToolbarProps> = ({
  range,
  lastDate,
  refreshing = false,
  onRangeChange,
  onIncrementalRefresh,
  onFullRefresh,
}) => {
  const isMobile = useIsMobile();

  return (
    <Space
      className="nav-toolbar"
      wrap
      size="middle"
      styles={{ root: { width: '100%', justifyContent: 'space-between' } }}
    >
      <Space wrap align="center">
        <Segmented
          value={range}
          onChange={(v) => onRangeChange(v as NavRangeKey)}
          options={NAV_RANGE_OPTIONS.map((o) => ({
            value: o.key,
            label: o.label,
          }))}
          size={isMobile ? 'small' : 'middle'}
        />
        {lastDate ? (
          <Typography.Text type="secondary" className="nav-toolbar__meta">
            最近收盘日：{lastDate}
          </Typography.Text>
        ) : null}
      </Space>
      <Space wrap>
        <Button
          type="primary"
          ghost
          icon={<ReloadOutlined />}
          loading={refreshing}
          onClick={onIncrementalRefresh}
          size={isMobile ? 'small' : 'middle'}
        >
          增量刷新
        </Button>
        <Button
          danger
          ghost
          loading={refreshing}
          onClick={onFullRefresh}
          size={isMobile ? 'small' : 'middle'}
        >
          全量刷新
        </Button>
      </Space>
    </Space>
  );
};
