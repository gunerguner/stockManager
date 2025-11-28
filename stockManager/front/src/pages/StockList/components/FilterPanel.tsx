import { Button, Row, Col, Checkbox } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

// ==================== 类型定义 ====================

type FilterPanelProps = {
  showAll: boolean;
  showConv: boolean;
  onRefresh: () => void;
  onShowAllChange: (checked: boolean) => void;
  onShowConvChange: (checked: boolean) => void;
};

// ==================== 组件 ====================

export const FilterPanel: React.FC<FilterPanelProps> = ({
  showAll,
  showConv,
  onRefresh,
  onShowAllChange,
  onShowConvChange,
}) => (
  <Row align="middle" gutter={[16, 16]}>
    <Col xs={24} sm={4} md={2}>
      <Button onClick={onRefresh} icon={<ReloadOutlined />} block>
        刷新
      </Button>
    </Col>
    <Col xs={12} sm={10} md={4} lg={{ offset: 15 }}>
      <Checkbox checked={showAll} onChange={(e) => onShowAllChange(e.target.checked)}>
        显示市值为零的股票
      </Checkbox>
    </Col>
    <Col xs={12} sm={10} md={3}>
      <Checkbox checked={showConv} onChange={(e) => onShowConvChange(e.target.checked)}>
        显示可转债
      </Checkbox>
    </Col>
  </Row>
);
