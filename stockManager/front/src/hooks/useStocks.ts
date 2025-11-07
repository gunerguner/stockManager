import { useEffect } from 'react';
import { useModel } from '@umijs/max';

/**
 * 股票数据 Hook
 * 自动处理股票数据的加载逻辑
 * 
 * @returns {Object} 返回股票数据和相关方法
 * @returns {API.StockData} stock - 股票数据
 * @returns {Function} fetchStockData - 手动刷新数据的方法
 * @returns {boolean} initialized - 是否已初始化
 */
export const useStocks = () => {
  const { stock, fetchStockData, initialized } = useModel('stocks');

  /**
   * 组件挂载时自动加载数据
   * 只在未初始化时加载，避免重复请求
   */
  useEffect(() => {
    if (!initialized) {
      fetchStockData();
    }
  }, [initialized, fetchStockData]);

  return {
    stock,
    fetchStockData,
    initialized,
  };
};

