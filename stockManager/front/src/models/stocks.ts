import { useState, useCallback } from 'react';
import { getStockList } from '@/services/api';
import { history } from '@umijs/max';

const loginPath = '/login';

// StockData 的默认初始值，确保 overall 和 stocks 始终存在
const defaultStockData: API.StockData = {
  stocks: [],
  overall: {
    offsetCurrent: 0,
    offsetTotal: 0,
    totalValue: 0,
    offsetCurrentRatio: '0%',
    offsetToday: 0,
    totalCash: 0,
    incomeCash: 0,
    originCash: 0,
    totalAsset: 0,
    totalCost: 0,
  },
};

export default () => {
  const [stock, setStock] = useState<API.StockData>(defaultStockData);
  const [initialized, setInitialized] = useState(false);

  /**
   * 获取股票数据
   */
  const fetchStockData = useCallback(async () => {
    try {
      const response = await getStockList();
      
      if (response.status === 1 && response.data) {
        setStock(response.data);
        setInitialized(true);
        return true;
      } else if (response.status === 302) {
        history.push(loginPath);
        return false;
      }
      return false;
    } catch (error) {
      console.error('获取股票数据失败:', error);
      return false;
    }
  }, []);

  /**
   * 手动设置股票数据（兼容旧的用法）
   */
  const setStockData = useCallback((stockData: API.StockData) => {
    setStock(stockData);
    setInitialized(true);
  }, []);

  /**
   * 重置股票数据状态
   * 用于用户登出或重新登录时清空数据
   */
  const resetStockData = useCallback(() => {
    setStock(defaultStockData);
    setInitialized(false);
  }, []);

  return { 
    stock, 
    initialized,
    setStockData,
    fetchStockData,
    resetStockData,
  };
};
