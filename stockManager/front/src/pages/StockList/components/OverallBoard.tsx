import { Statistic, Row, Col, InputNumber, Form, App, Divider } from 'antd';
import { useState } from 'react';
import { UpOutlined, DownOutlined } from '@ant-design/icons';
import { updateIncomeCash } from '@/services/api';
import { colorFromValue } from '@/utils/renderTool';
import { useIsMobile } from '@/hooks/useIsMobile';
import { RESPONSE_STATUS } from '@/utils/constants';
import './index.less';

// ==================== 类型定义 ====================

type OverallBoardProps = {
  data: API.Overall;
  onModifySuccess?: () => void;
};

type StatisticItemConfig = {
  key: keyof API.Overall;
  title: string;
  showColor?: boolean;
  isMain?: boolean;
};

// ==================== 配置 ====================

/** 主要统计项（始终显示） */
const MAIN_STATISTICS: StatisticItemConfig[] = [
  { key: 'offsetToday', title: '当日盈亏', showColor: true, isMain: true },
  { key: 'totalAsset', title: '总资产', isMain: true },
];

/** 展开后的统计项 */
const EXPANDED_STATISTICS: StatisticItemConfig[] = [
  { key: 'offsetCurrent', title: '浮动盈亏', showColor: true },
  { key: 'offsetTotal', title: '累计盈亏', showColor: true },
  { key: 'totalValue', title: '市值', showColor: true },
  { key: 'totalCash', title: '现金' },
  { key: 'incomeCash', title: '其它现金收入' },
  { key: 'originCash', title: '本金' },
];

// ==================== 子组件 ====================

type StatisticItemProps = {
  title: string;
  value: number;
  showColor?: boolean;
  isMain?: boolean;
  onClick?: () => void;
};

const StatisticItem: React.FC<StatisticItemProps> = ({
  title,
  value,
  showColor = false,
  isMain = false,
  onClick,
}) => {
  const isMobile = useIsMobile();
  const colSpan = isMobile ? 12 : 6;
  const clickable = !!onClick;

  // 统一通过 Statistic 的 styles 控制样式，而不是依赖 CSS 选择器
  const titleStyle: React.CSSProperties = {
    fontSize: isMobile ? 12 : isMain ? 14 : 13,
    marginBottom: isMobile ? (isMain ? 6 : 4) : isMain ? 8 : 4,
  };

  const contentStyle: React.CSSProperties = {
    fontWeight: isMain ? 'bold' : 'normal',
    fontSize: isMobile ? (isMain ? 24 : 18) : isMain ? 28 : 20,
    lineHeight: isMain && !isMobile ? 1.2 : 1.2,
    ...(showColor && { color: colorFromValue(value) }),
    ...(clickable && { color: '#1890ff' }),
  };

  return (
    <Col span={colSpan} onClick={onClick} style={clickable ? { cursor: 'pointer' } : undefined}>
      <Statistic
        title={title}
        value={value}
        precision={2}
        styles={{ title: titleStyle, content: contentStyle }}
      />
    </Col>
  );
};

// ==================== 组件 ====================

export const OverallBoard: React.FC<OverallBoardProps> = ({ data, onModifySuccess }) => {
  const [form] = Form.useForm();
  const { modal } = App.useApp();
  const [isExpanded, setIsExpanded] = useState(false);

  /** 处理编辑现金收入 */
  const handleEditIncomeCash = () => {
    const initialIncomeCash = data.incomeCash || 0;
    const initialTotalAsset = data.totalAsset || 0;
    const fixedPart = initialTotalAsset - initialIncomeCash;

    form.setFieldsValue({ incomeCash: initialIncomeCash, totalAsset: initialTotalAsset });

    modal.confirm({
      title: '编辑现金收入',
      icon: null,
      content: (
        <Form className="form-container" form={form} layout="vertical" name="incomeCash">
          <Form.Item label="现金收入" name="incomeCash" rules={[{ required: true, message: '请输入现金收入' }]}>
            <InputNumber
              style={{ width: '100%' }}
              precision={2}
              step={0.01}
              onChange={(v) => form.setFieldsValue({ totalAsset: fixedPart + ((v as number) || 0) })}
            />
          </Form.Item>
          <Form.Item label="总资产" name="totalAsset" rules={[{ required: true, message: '请输入总资产' }]}>
            <InputNumber
              style={{ width: '100%' }}
              precision={2}
              step={0.01}
              onChange={(v) => form.setFieldsValue({ incomeCash: ((v as number) || 0) - fixedPart })}
            />
          </Form.Item>
        </Form>
      ),
      onOk: async () => {
        const { incomeCash } = await form.validateFields();
        const response = await updateIncomeCash(incomeCash);
        if (response.status === RESPONSE_STATUS.SUCCESS) {
          onModifySuccess?.();
        }
      },
    });
  };

  /** 可点击项的回调映射 */
  const clickHandlers: Partial<Record<keyof API.Overall, () => void>> = {
    incomeCash: handleEditIncomeCash,
  };

  /** 渲染统计项列表 */
  const renderStatistics = (configs: StatisticItemConfig[]) =>
    configs.map((config) => (
      <StatisticItem
        key={config.key}
        title={config.title}
        value={(data[config.key] as number) || 0}
        showColor={config.showColor}
        isMain={config.isMain}
        onClick={clickHandlers[config.key]}
      />
    ));

  return (
    <div className="overall-board-wrapper">
      <Row gutter={[16, 16]}>{renderStatistics(MAIN_STATISTICS)}</Row>

      <div
        className={`expand-divider-wrapper ${isExpanded ? 'expanded' : 'collapsed'}`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Divider
          className="expand-divider"
          styles={{
            root: { margin: 0 },
            content: { margin: '0 8px' },
          }}
        >
          {isExpanded ? <UpOutlined className="expand-icon" /> : <DownOutlined className="expand-icon" />}
        </Divider>
      </div>

      {isExpanded && (
        <Row gutter={[16, 16]} className="expanded-statistics-row">
          {renderStatistics(EXPANDED_STATISTICS)}
        </Row>
      )}
    </div>
  );
};
