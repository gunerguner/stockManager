import { useState, useEffect } from 'react';
import { Tag, Space } from 'antd';
import { getTradingStatus } from '@/services/api';
import { useIsMobile } from '@/hooks/useIsMobile';

// ==================== 组件 ====================

const TradingTime: React.FC = () => {
  const [statuses, setStatuses] = useState<API.TradingTimeStatus[]>([]);
  const isMobile = useIsMobile();

  useEffect(() => {
    let active = true;

    const fetchStatus = async () => {
      try {
        const res = await getTradingStatus();
        if (!active) return;
        setStatuses(res.data ?? []);
      } catch (err) {
        // 吞错：保留上一次状态，避免 60s 轮询在 401/网络抖动时清空 Tag 或触发全局错误提示
        console.warn('fetch trading status failed', err);
      }
    };

    fetchStatus();
    const intervalId = setInterval(fetchStatus, 60 * 1000);
    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  if (statuses.length === 0) return null;

  return (
    <Space size={4} wrap>
      {statuses.map((status) => (
        <Tag
          key={status.market}
          color={status.isTrading ? 'orange' : 'purple'}
          style={{ margin: 0, fontSize: isMobile ? 11 : undefined }}
        >
          {status.message}
        </Tag>
      ))}
    </Space>
  );
};

export default TradingTime;
