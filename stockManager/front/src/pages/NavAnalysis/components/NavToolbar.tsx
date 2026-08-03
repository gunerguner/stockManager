import { Button, Segmented, Space, Typography } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useIsMobile } from '@/hooks/useIsMobile';
import { NAV_RANGE_OPTIONS, type NavRangeKey } from './navStat';

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
      wrap
      size="middle"
      style={{
        width: '100%',
        justifyContent: 'space-between',
        marginBottom: isMobile ? 12 : 16,
      }}
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
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
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
