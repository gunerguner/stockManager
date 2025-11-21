/**
 * 交易时间提示组件
 * 显示当前是否在交易时间内，以及距离收盘/开盘的时间
 */

import React, { useState, useEffect } from 'react';
import { Tag } from 'antd';
import { getTradingTimeStatus, TradingTimeStatus } from '@/utils';
import { useIsMobile } from '@/hooks/useIsMobile';

/**
 * 交易时间提示组件
 */
const TradingTime: React.FC = () => {
  const [status, setStatus] = useState<TradingTimeStatus>(() => {
    return getTradingTimeStatus();
  });
  const isMobile = useIsMobile();

  useEffect(() => {
    // 更新状态的函数
    const updateStatus = () => {
      setStatus(getTradingTimeStatus());
    };
    
    // 立即更新一次状态
    updateStatus();
    
    // 每分钟更新一次
    const intervalId = setInterval(updateStatus, 60 * 1000);
    
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const tagColor = status.isTrading ? 'orange' : 'purple';

  return (
    <Tag color={tagColor} style={{ margin: 0, fontSize: isMobile ? '11px' : undefined }}>
      {status.message}
    </Tag>
  );
};

export default TradingTime;

