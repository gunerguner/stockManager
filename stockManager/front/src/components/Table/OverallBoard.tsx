import { Statistic, Row, Col, Input, Form, App, Divider } from 'antd';
import React, { useState } from 'react';
import { UpOutlined, DownOutlined } from '@ant-design/icons';
import { updateIncomeCash } from '@/services/api';
import { colorFromValue } from '@/utils';
import { useIsMobile } from '@/hooks/useIsMobile';
import { RESPONSE_STATUS } from '@/utils/constants';
import './index.less';

export type OverallBoardProps = {
  data: API.Overall;
  completion?: (success: boolean) => void;
};

/**
 * 统计项基础配置（共享字段）
 */
type StatisticItemBase = {
  title: string;
  showColor?: boolean;
  isMain?: boolean;
  suffix?: React.ReactNode;
};

/**
 * 统计项配置类型（用于配置数组）
 */
type StatisticItemConfig = StatisticItemBase & {
  key: keyof API.Overall;
};

/**
 * 统计项组件 Props（用于组件渲染）
 */
type StatisticItemProps = StatisticItemBase & {
  value: number;
};

/**
 * 统计项组件 - 抽取重复的 Statistic 定义
 */
const StatisticItem: React.FC<StatisticItemProps> = ({
  title,
  value,
  showColor = false,
  isMain = false,
  suffix,
}) => {
  const isMobile = useIsMobile();
  // 每行显示的列数（移动端2列，桌面端4列）
  const colSpan = isMobile ? 12 : 6;

  const valueStyle: React.CSSProperties = {
    fontWeight: isMain ? 'bold' : 'normal',
    ...(showColor && { color: colorFromValue(value) }),
  };

  return (
    <Col span={colSpan}>
      <Statistic
        title={title}
        value={value}
        precision={2}
        className={isMain ? 'main-statistic' : ''}
        valueStyle={valueStyle}
        suffix={suffix}
      />
    </Col>
  );
};

export const OverallBoard: React.FC<OverallBoardProps> = (props) => {
  const [form] = Form.useForm();
  const { modal } = App.useApp();
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const { data } = props;

  /**
   * 处理编辑现金收入
   */
  const handleEditIncomeCash = (): void => {
    modal.confirm({
      title: '编辑现金收入',
      content: (
        <Form className="form-container" form={form} layout="vertical" name="incomeCash">
          <Form.Item
            name="incomeCash"
            rules={[{ required: true, message: '请输入现金收入' }]}
          >
            <Input type="number" defaultValue={data.incomeCash || 0} />
          </Form.Item>
        </Form>
      ),
      onOk: async () => {
        const { incomeCash } = await form.validateFields();
        const response = await updateIncomeCash(incomeCash);
        if (props.completion) {
          props.completion(response.status === RESPONSE_STATUS.SUCCESS);
        }
      },
    });
  };

  /**
   * 切换展开/折叠状态
   */
  const toggleExpand = (): void => {
    setIsExpanded(!isExpanded);
  };

  /**
   * 主要统计项配置（始终显示）
   */
  const mainStatistics: StatisticItemConfig[] = [
    { key: 'offsetToday', title: '当日盈亏', showColor: true, isMain: true },
    { key: 'totalAsset', title: '总资产', isMain: true },
  ];

  /**
   * 展开后的统计项配置
   */
  const expandedStatistics: StatisticItemConfig[] = [
    { key: 'offsetCurrent', title: '浮动盈亏', showColor: true },
    { key: 'offsetTotal', title: '累计盈亏', showColor: true },
    { key: 'totalValue', title: '市值', showColor: true },
    { key: 'totalCash', title: '现金' },
    {
      key: 'incomeCash',
      title: '其它现金收入',
      suffix: (
        <a
          onClick={handleEditIncomeCash}
          style={{ fontSize: '12px', marginLeft: '8px' }}
        >
          编辑
        </a>
      ),
    },
    { key: 'originCash', title: '本金' },
  ];

  /**
   * 渲染统计项列表
   */
  const renderStatistics = (configs: StatisticItemConfig[]): React.ReactNode => {
    return configs.map((config) => {
      const value = (data[config.key] as number) || 0;
      return (
        <StatisticItem
          key={config.key}
          title={config.title}
          value={value}
          showColor={config.showColor}
          isMain={config.isMain}
          suffix={config.suffix}
        />
      );
    });
  };

  return (
    <div className="overall-board-wrapper">
      <Row gutter={[16, 16]}>{renderStatistics(mainStatistics)}</Row>

      {/* Divider + 箭头 - 表示可展开/折叠 */}
      <div
        className={`expand-divider-wrapper ${isExpanded ? 'expanded' : 'collapsed'}`}
        onClick={toggleExpand}
      >
        <Divider className="expand-divider">
          {isExpanded ? (
            <UpOutlined className="expand-icon" />
          ) : (
            <DownOutlined className="expand-icon" />
          )}
        </Divider>
      </div>

      {/* 其他指标 - 根据展开状态显示 */}
      {isExpanded && (
        <Row gutter={[16, 16]} className="expanded-statistics-row">
          {renderStatistics(expandedStatistics)}
        </Row>
      )}
    </div>
  );
};
