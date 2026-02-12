import { useState, useCallback } from 'react';
import { getStockList } from '@/services/api';
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
  const [initialized, setInitialized] = useState(false);

  const fetchStockData = useCallback(async () => {
    try {
      const response = await getStockList();

      if (response.status === RESPONSE_STATUS.SUCCESS && response.data) {
        setStock(response.data);
        setInitialized(true);
        return true;
      }
      if (response.status === RESPONSE_STATUS.UNAUTHORIZED) {
        history.push('/login');
      }
      return false;
    } catch (error) {
      // 错误由全局 errorHandler/responseInterceptor 处理
      return false;
    }
  }, []);

  const setStockData = useCallback((data: API.StockData) => {
    setStock(data);
    setInitialized(true);
  }, []);

  const resetStockData = useCallback(() => {
    setStock(DEFAULT_STOCK_DATA);
    setInitialized(false);
  }, []);

  return { stock, initialized, setStockData, fetchStockData, resetStockData };
};
