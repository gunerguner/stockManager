import { useState, useCallback, useEffect } from 'react';
import { getStockList } from '@/services/api';
import { history } from '@umijs/max';

export default () => {
  const [stock, setStock] = useState({} as API.StockData);
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
        history.push('/login');
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
   * 初始化时自动加载数据
   */
  useEffect(() => {
    // 只在首次加载且未初始化时自动获取数据
    if (!initialized) {
      fetchStockData();
    }
  }, [initialized, fetchStockData]);

  return { 
    stock, 
    initialized,
    setStockData,
    fetchStockData,
  };
};
