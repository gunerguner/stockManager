import { useEffect } from 'react';
import { useModel } from '@umijs/max';

/** 关注列表 Hook - 自动处理数据加载 */
export const useWatchlist = () => {
  const { list, fetchWatchlist, setItemHidden, initialized, loading } = useModel('watchlist');

  useEffect(() => {
    if (!initialized) fetchWatchlist();
  }, [initialized, fetchWatchlist]);

  return { list, fetchWatchlist, setItemHidden, initialized, loading };
};
