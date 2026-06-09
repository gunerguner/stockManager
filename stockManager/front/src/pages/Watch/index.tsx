import { ReloadOutlined } from '@ant-design/icons';
import { FloatButton, Button } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useWatchlist } from '@/hooks/useWatchlist';
import { WatchTable } from './components/WatchTable';

const Watch: React.FC = () => {
  const { list, fetchWatchlist, loading } = useWatchlist();

  return (
    <>
      <FloatButton.BackTop />
      <div style={{ borderRadius: 8, padding: 16 }}>
        <ProCard
          extra={
            <Button icon={<ReloadOutlined />} onClick={fetchWatchlist} loading={loading}>
              刷新
            </Button>
          }
        >
          <WatchTable data={list} loading={loading} />
        </ProCard>
      </div>
    </>
  );
};

export default Watch;
