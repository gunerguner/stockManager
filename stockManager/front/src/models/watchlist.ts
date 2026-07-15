import { useCallback, useState } from 'react';
import { notification } from 'antd';
import { getWatchlist, updateWatchHidden } from '@/services/api';
import { hasApiData, isApiSuccess, isUnauthorized } from '@/utils/api';

export default () => {
  const [list, setList] = useState<API.WatchItem[]>([]);
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchWatchlist = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getWatchlist({
        timeout: 30000,
        skipErrorHandler: true,
      });
      if (hasApiData(res)) {
        setList(res.data);
      }
      if (isUnauthorized(res)) {
        return false;
      }
      setInitialized(true);
      return true;
    } catch {
      notification.error({
        title: '加载失败',
        description: '获取关注列表失败，请稍后重试',
      });
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const setItemHidden = useCallback(async (code: string, hidden: boolean) => {
    try {
      const res = await updateWatchHidden(code, hidden, { skipErrorHandler: true });
      if (!isApiSuccess(res)) {
        notification.error({
          title: '操作失败',
          description: res.message || '更新隐藏状态失败，请稍后重试',
        });
        return false;
      }
      setList((prev) =>
        prev.map((item) => (item.code === code ? { ...item, hidden } : item)),
      );
      return true;
    } catch {
      notification.error({
        title: '操作失败',
        description: '更新隐藏状态失败，请稍后重试',
      });
      return false;
    }
  }, []);

  const resetWatchlist = useCallback(() => {
    setList([]);
    setInitialized(false);
    setLoading(false);
  }, []);

  return {
    list,
    initialized,
    loading,
    fetchWatchlist,
    setItemHidden,
    resetWatchlist,
  };
};
