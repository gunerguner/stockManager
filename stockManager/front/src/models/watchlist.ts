import { useCallback, useState } from 'react';
import { notification } from 'antd';
import { getWatchlist } from '@/services/api';
import { RESPONSE_STATUS } from '@/utils/constants';

export default () => {
  const [list, setList] = useState<API.WatchItem[]>([]);
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchWatchlist = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getWatchlist();
      if (res.status === RESPONSE_STATUS.SUCCESS && res.data) {
        setList(res.data);
      }
      if (res.status === RESPONSE_STATUS.UNAUTHORIZED) {
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

  const resetWatchlist = useCallback(() => {
    setList([]);
    setInitialized(false);
    setLoading(false);
  }, []);

  return { list, initialized, loading, fetchWatchlist, resetWatchlist };
};
