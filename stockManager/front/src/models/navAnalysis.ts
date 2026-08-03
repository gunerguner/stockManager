import { useCallback, useState } from 'react';
import { notification } from 'antd';
import { getNavAnalysis, refreshNav } from '@/services/api';
import { hasApiData, isApiSuccess, isUnauthorized } from '@/utils/api';

export default () => {
  const [data, setData] = useState<API.NavAnalysisData | null>(null);
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNavAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getNavAnalysis({
        timeout: 30000,
        skipErrorHandler: true,
      });
      if (hasApiData(res) && res.data) {
        setData(res.data);
      } else {
        setData(null);
      }
      if (isUnauthorized(res)) {
        return false;
      }
      setInitialized(true);
      return true;
    } catch {
      notification.error({
        title: '加载失败',
        description: '获取净值分析失败，请稍后重试',
      });
      setData(null);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshNavData = useCallback(
    async (mode: 'incremental' | 'full') => {
      setRefreshing(true);
      try {
        const res = await refreshNav(mode, {
          timeout: 300000,
          skipErrorHandler: true,
        });
        if (isApiSuccess(res)) {
          notification.success({
            title: '刷新成功',
            description:
              mode === 'full'
                ? `全量刷新完成，共 ${res.data?.pointCount ?? 0} 个交易日`
                : `增量刷新完成，写入 ${res.data?.written ?? 0} 天`,
          });
          await fetchNavAnalysis();
          return true;
        }
        notification.error({
          title: '刷新失败',
          description: res.message || '刷新净值失败，请稍后重试',
        });
        return false;
      } catch {
        notification.error({
          title: '刷新失败',
          description: '刷新净值失败，请稍后重试',
        });
        return false;
      } finally {
        setRefreshing(false);
      }
    },
    [fetchNavAnalysis],
  );

  const resetNavAnalysis = useCallback(() => {
    setData(null);
    setInitialized(false);
    setLoading(false);
    setRefreshing(false);
  }, []);

  return {
    data,
    initialized,
    loading,
    refreshing,
    fetchNavAnalysis,
    refreshNavData,
    resetNavAnalysis,
  };
};
