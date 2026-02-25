import { useState, useCallback } from 'react';
import { getStocks, getOperations } from '@/services/api';
import { history } from '@umijs/max';
import { RESPONSE_STATUS } from '@/utils/constants';

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
    xirrAnnualized: '0.00%',
  },
};

// ==================== Model ====================

export default () => {
  const [stock, setStock] = useState<API.StockData>(DEFAULT_STOCK_DATA);
  const [operations, setOperations] = useState<Record<string, API.Operation[]>>({});
  const [initialized, setInitialized] = useState(false);

  const fetchStockData = useCallback(async () => {
    try {
      // 并行请求两个接口
      const [stocksResponse, operationsResponse] = await Promise.all([
        getStocks(),
        getOperations(),
      ]);

      if (stocksResponse.status === RESPONSE_STATUS.SUCCESS && stocksResponse.data) {
        setStock(stocksResponse.data);
      }

      if (operationsResponse.status === RESPONSE_STATUS.SUCCESS && operationsResponse.data) {
        setOperations(operationsResponse.data);
      }

      if (stocksResponse.status === RESPONSE_STATUS.UNAUTHORIZED) {
        history.push('/login');
        return false;
      }

      setInitialized(true);
      return true;
    } catch (error) {
      return false;
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
  }, []);

  return { stock, operations, initialized, setStockData, fetchStockData, resetStockData };
};
