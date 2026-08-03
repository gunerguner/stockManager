import { useEffect } from 'react';
import { FloatButton, theme } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { WatchBoard } from './components/WatchBoard';
import '@/components/Common/index.less';

const Watch: React.FC = () => {
  const { list, fetchWatchlist, setItemHidden, initialized, loading } =
    useModel('watchlist');
  const { token } = theme.useToken();

  useEffect(() => {
    if (!initialized) void fetchWatchlist();
  }, [initialized, fetchWatchlist]);

  return (
    <>
      <FloatButton.BackTop />
      <div className="page-container">
        <ProCard
          styles={{
            root: {
              background: token.colorBgContainer,
              borderColor: token.colorBorderSecondary,
            },
          }}
        >
          <WatchBoard
            list={list}
            loading={loading}
            onRefresh={fetchWatchlist}
            onSetHidden={setItemHidden}
          />
        </ProCard>
      </div>
    </>
  );
};

export default Watch;
