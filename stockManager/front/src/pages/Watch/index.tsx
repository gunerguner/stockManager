import { ReloadOutlined } from '@ant-design/icons';
import { FloatButton, Button, Row, Col } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useWatchlist } from '@/hooks/useWatchlist';
import { WatchTable } from './components/WatchTable';

const Watch: React.FC = () => {
  const { list, fetchWatchlist, loading } = useWatchlist();

  return (
    <>
      <FloatButton.BackTop />
      <div style={{ borderRadius: 8, padding: 16 }}>
        <ProCard>
          <Row align="middle" gutter={[16, 16]} style={{ marginTop: 16, marginBottom: 16 }}>
            <Col xs={24} sm={4} md={2}>
              <Button
                type="primary"
                ghost
                icon={<ReloadOutlined />}
                onClick={fetchWatchlist}
                loading={loading}
                block
              >
                刷新
              </Button>
            </Col>
          </Row>
          <WatchTable data={list} loading={loading} />
        </ProCard>
      </div>
    </>
  );
};

export default Watch;
