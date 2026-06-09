import { useState, useEffect } from 'react';
import { Tag, Space } from 'antd';
import { getAllTradingTimeStatuses, TradingTimeStatus } from '@/utils/tradingTime';
import { useIsMobile } from '@/hooks/useIsMobile';

// ==================== 组件 ====================

const TradingTime: React.FC = () => {
  const [statuses, setStatuses] = useState<TradingTimeStatus[]>(() =>
    getAllTradingTimeStatuses(),
  );
  const isMobile = useIsMobile();

  useEffect(() => {
    const updateStatus = () => setStatuses(getAllTradingTimeStatuses());
    updateStatus();

    const intervalId = setInterval(updateStatus, 60 * 1000);
    return () => clearInterval(intervalId);
  }, []);

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
