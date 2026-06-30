import { Button, Row, Col, Checkbox, Space } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useIsMobile } from '@/hooks/useIsMobile';

type StockListToolbarProps = {
  showAll: boolean;
  showConv: boolean;
  onRefresh: () => void;
  onShowAllChange: (checked: boolean) => void;
  onShowConvChange: (checked: boolean) => void;
};

export const StockListToolbar: React.FC<StockListToolbarProps> = ({
  showAll,
  showConv,
  onRefresh,
  onShowAllChange,
  onShowConvChange,
}) => {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <Row align="middle" gutter={[8, 8]} style={{ marginTop: 12, marginBottom: 12 }}>
        <Col span={8}>
          <Button type="primary" ghost onClick={onRefresh} icon={<ReloadOutlined />} block size="small">
            刷新
          </Button>
        </Col>
        <Col span={16}>
          <Space wrap size={[8, 4]}>
            <Checkbox
              checked={showAll}
              onChange={(e) => onShowAllChange(e.target.checked)}
              style={{ fontSize: 12 }}
            >
              显示市值为零
            </Checkbox>
            <Checkbox
              checked={showConv}
              onChange={(e) => onShowConvChange(e.target.checked)}
              style={{ fontSize: 12 }}
            >
              显示可转债
            </Checkbox>
          </Space>
        </Col>
      </Row>
    );
  }

  return (
    <Row align="middle" gutter={[16, 16]} style={{ marginTop: 16, marginBottom: 16 }}>
      <Col sm={4} md={2}>
        <Button type="primary" ghost onClick={onRefresh} icon={<ReloadOutlined />} block>
          刷新
        </Button>
      </Col>
      <Col sm={20} md={{ offset: 14, span: 8 }}>
        <Space wrap size={[16, 8]}>
          <Checkbox checked={showAll} onChange={(e) => onShowAllChange(e.target.checked)}>
            显示市值为零的股票
          </Checkbox>
          <Checkbox checked={showConv} onChange={(e) => onShowConvChange(e.target.checked)}>
            显示可转债
          </Checkbox>
        </Space>
      </Col>
    </Row>
  );
};
