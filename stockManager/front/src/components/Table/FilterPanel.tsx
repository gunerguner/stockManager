import { Button, Row, Col, Checkbox } from 'antd';
import React from 'react';
import { ReloadOutlined } from '@ant-design/icons';

export type FilterPanelProps = {
  /** 是否显示市值为零的股票 */
  showAll: boolean;
  /** 是否显示可转债 */
  showConv: boolean;
  /** 刷新数据回调 */
  onRefresh: () => void;
  /** 显示市值为零的股票变化回调 */
  onShowAllChange: (checked: boolean) => void;
  /** 显示可转债变化回调 */
  onShowConvChange: (checked: boolean) => void;
};

/**
 * 筛选控制面板组件
 * 提供刷新按钮和筛选选项
 */
export const FilterPanel: React.FC<FilterPanelProps> = ({
  showAll,
  showConv,
  onRefresh,
  onShowAllChange,
  onShowConvChange,
}) => {
  return (
    <Row align="middle" gutter={[16, 16]}>
      <Col xs={24} sm={4} md={2}>
        <Button onClick={onRefresh} icon={<ReloadOutlined />} block>
          刷新
        </Button>
      </Col>
      <Col xs={12} sm={10} md={4} offset={0} lg={{ offset: 15 }}>
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
};

