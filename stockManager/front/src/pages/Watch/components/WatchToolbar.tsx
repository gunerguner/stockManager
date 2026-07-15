import { Button, Row, Col } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useIsMobile } from '@/hooks/useIsMobile';

type WatchToolbarProps = {
  loading?: boolean;
  onRefresh: () => void;
};

export const WatchToolbar: React.FC<WatchToolbarProps> = ({ loading = false, onRefresh }) => {
  const isMobile = useIsMobile();

  return (
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
          onClick={onRefresh}
          loading={loading}
          block
        >
          刷新
        </Button>
      </Col>
    </Row>
  );
};
