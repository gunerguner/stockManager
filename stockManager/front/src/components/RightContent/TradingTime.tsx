import { useState, useEffect } from 'react';
import { Tag } from 'antd';
import { getTradingTimeStatus, TradingTimeStatus } from '@/utils/tradingTime';
import { useIsMobile } from '@/hooks/useIsMobile';

// ==================== 组件 ====================

const TradingTime: React.FC = () => {
  const [status, setStatus] = useState<TradingTimeStatus>(getTradingTimeStatus);
  const isMobile = useIsMobile();

  useEffect(() => {
    const updateStatus = () => setStatus(getTradingTimeStatus());
    updateStatus();

    const intervalId = setInterval(updateStatus, 60 * 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <Tag
      color={status.isTrading ? 'orange' : 'purple'}
      style={{ margin: 0, fontSize: isMobile ? '11px' : undefined }}
    >
      {status.message}
    </Tag>
  );
};

export default TradingTime;
