import { useState } from 'react';
import { DownOutlined, UpOutlined } from '@ant-design/icons';
import { Divider, theme } from 'antd';
import { WatchTable } from './WatchTable';
import './index.less';

type HiddenWatchSectionProps = {
  data: API.WatchItem[];
  loading?: boolean;
  onToggleHidden?: (record: API.WatchItem, nextHidden: boolean) => Promise<boolean>;
};

export const HiddenWatchSection: React.FC<HiddenWatchSectionProps> = ({
  data,
  loading = false,
  onToggleHidden,
}) => {
  const { token } = theme.useToken();
  const [expanded, setExpanded] = useState(false);

  if (data.length === 0) return null;

  return (
    <div className="watch-hidden-section">
      <div
        className={`expand-divider-wrapper ${expanded ? 'expanded' : 'collapsed'}`}
        onClick={() => setExpanded((v) => !v)}
        style={
          {
            '--divider-color': token.colorBorderSecondary,
            '--divider-hover-color': token.colorPrimary,
          } as React.CSSProperties
        }
      >
        <Divider
          className="expand-divider"
          styles={{
            root: { margin: 0 },
            content: { margin: '0 8px' },
          }}
        >
          <span className="expand-label">
            隐藏列表 ({data.length})
            {expanded ? (
              <UpOutlined className="expand-icon" />
            ) : (
              <DownOutlined className="expand-icon" />
            )}
          </span>
        </Divider>
      </div>

      {expanded && (
        <WatchTable data={data} loading={loading} onToggleHidden={onToggleHidden} />
      )}
    </div>
  );
};
