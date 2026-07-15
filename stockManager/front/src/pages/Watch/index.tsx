import { FloatButton, theme } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useWatchlist } from '@/hooks/useWatchlist';
import { WatchBoard } from './components/WatchBoard';
import '@/components/Common/index.less';

const Watch: React.FC = () => {
  const { list, fetchWatchlist, setItemHidden, loading } = useWatchlist();
  const { token } = theme.useToken();

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
