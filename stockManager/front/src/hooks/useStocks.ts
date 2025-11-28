import { useEffect } from 'react';
import { useModel } from '@umijs/max';

/** 股票数据 Hook - 自动处理数据加载 */
export const useStocks = () => {
  const { stock, fetchStockData, initialized } = useModel('stocks');

  useEffect(() => {
    if (!initialized) fetchStockData();
  }, [initialized, fetchStockData]);

  return { stock, fetchStockData, initialized };
};
