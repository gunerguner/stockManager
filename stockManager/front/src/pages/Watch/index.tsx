import { ReloadOutlined } from '@ant-design/icons';
import { FloatButton, Button, Row, Col, theme } from 'antd';
import { ProCard } from '@ant-design/pro-components';
import { useWatchlist } from '@/hooks/useWatchlist';
import { useIsMobile } from '@/hooks/useIsMobile';
import { WatchTable } from './components/WatchTable';
import '@/components/Common/index.less';

const Watch: React.FC = () => {
  const { list, fetchWatchlist, loading } = useWatchlist();
  const isMobile = useIsMobile();
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
          <Row
            align="middle"
            gutter={[16, 8]}
            style={{ marginTop: isMobile ? 0 : 16, marginBottom: isMobile ? 12 : 16 }}
          >
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
