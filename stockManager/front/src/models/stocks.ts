import { useState, useCallback } from 'react';
import { notification } from 'antd';
import { getStocks, getOperations } from '@/services/api';
import { hasApiData, isUnauthorized } from '@/utils/api';

// ==================== 配置 ====================

const DEFAULT_STOCK_DATA: API.StockData = {
  stocks: [],
  overall: {
    offsetCurrent: 0,
    offsetTotal: 0,
    totalValue: 0,
    offsetToday: 0,
    totalCash: 0,
    incomeCash: 0,
    originCash: 0,
    totalAsset: 0,
    totalCost: 0,
    cashFlowList: [],
    xirrAnnualized: 0,
  },
};

// ==================== Model ====================

export default () => {
  const [stock, setStock] = useState<API.StockData>(DEFAULT_STOCK_DATA);
  const [operations, setOperations] = useState<Record<string, API.Operation[]>>({});
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchStockData = useCallback(async () => {
    setLoading(true);
    try {
      const [stocksResponse, operationsResponse] = await Promise.all([
        getStocks(),
        getOperations(),
      ]);

      if (hasApiData(stocksResponse)) {
        setStock(stocksResponse.data);
      }

      if (hasApiData(operationsResponse)) {
        setOperations(operationsResponse.data);
      }

      if (isUnauthorized(stocksResponse)) {
        return false;
      }

      setInitialized(true);
      return true;
    } catch {
      notification.error({
        title: '加载失败',
        description: '获取持仓数据失败，请稍后重试',
      });
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const setStockData = useCallback((data: API.StockData) => {
    setStock(data);
    setInitialized(true);
  }, []);

  const resetStockData = useCallback(() => {
    setStock(DEFAULT_STOCK_DATA);
    setOperations({});
    setInitialized(false);
    setLoading(false);
  }, []);

  return { stock, operations, initialized, loading, setStockData, fetchStockData, resetStockData };
};
