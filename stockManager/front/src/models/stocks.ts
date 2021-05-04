import { useState, useCallback } from 'react';

export default () => {
  const [stock, setStock] = useState({} as API.StockData);

  const setStockData = useCallback((stockData: API.StockData) => {
    setStock(stockData);
  }, []);

  return { stock, setStockData };
};
