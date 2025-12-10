import { Statistic, Row, Col, InputNumber, Form, App, Divider } from 'antd';
import { useState } from 'react';
import { UpOutlined, DownOutlined } from '@ant-design/icons';
import { updateIncomeCash } from '@/services/api';
import { colorFromValue } from '@/utils/renderTool';
import { useIsMobile } from '@/hooks/useIsMobile';
import { RESPONSE_STATUS } from '@/utils/constants';
import { useCashFlowModal } from '@/components/Common/CashFlowModal';
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
  { key: 'originCash', title: '总入金' },
];

// ==================== 子组件 ====================

type StatisticItemProps = StatisticItemConfig & {
  value: number;
  onClick?: () => void;
};

const StatisticItem: React.FC<StatisticItemProps> = ({
  title,
  value,
  showColor,
  isMain,
  onClick,
}) => {
  const isMobile = useIsMobile();
  const clickable = !!onClick;
  const styles = {
    title: {
      fontSize: isMobile ? 12 : isMain ? 14 : 13,
      marginBottom: isMobile ? (isMain ? 6 : 4) : isMain ? 8 : 4,
    },
    content: {
      fontWeight: isMain ? 'bold' : 'normal',
      fontSize: isMobile ? (isMain ? 24 : 18) : isMain ? 28 : 20,
      lineHeight: 1.2,
      ...(showColor && { color: colorFromValue(value) }),
      ...(clickable && { color: '#1890ff' }),
    },
  };

  return (
    <Col span={isMobile ? 12 : 6} onClick={onClick} style={clickable ? { cursor: 'pointer' } : undefined}>
      <Statistic title={title} value={value} precision={2} styles={styles} />
    </Col>
  );
};

// ==================== 组件 ====================

export const OverallBoard: React.FC<OverallBoardProps> = ({ data, onModifySuccess }) => {
  const [form] = Form.useForm();
  const { modal } = App.useApp();
  const [isExpanded, setIsExpanded] = useState(false);
  const { showCashFlow } = useCashFlowModal();
  const isMobile = useIsMobile();

  /** 可点击项的回调映射 */
  const clickHandlers: Partial<Record<keyof API.Overall, () => void>> = {
    incomeCash: () => {

      const totalAsset = data.totalAsset || 0;
      const incomeCash = data.incomeCash || 0;
      form.setFieldsValue({ incomeCash: incomeCash, totalAsset: totalAsset });
      
      const fixedPart = totalAsset - incomeCash;

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
          if (response.status === RESPONSE_STATUS.SUCCESS) onModifySuccess?.();
        },
      });
    },
    originCash: () => showCashFlow({ totalCashIn: data.originCash || 0, cashFlowList: data.cashFlowList || [] }),
  };

  /** 渲染统计项列表 */
  const renderStatistics = (configs: StatisticItemConfig[]) =>
    configs.map(({ key, ...config }) => (
      <StatisticItem
        key={key}
        {...config}
        value={(data[key] as number) || 0}
        onClick={clickHandlers[key]}
      />
    ));

  return (
    <div className="overall-board-wrapper">
      <Row gutter={[16, 16]}>{renderStatistics(MAIN_STATISTICS)}</Row>

      <div className={`expand-divider-wrapper ${isExpanded ? 'expanded' : 'collapsed'}`} onClick={() => setIsExpanded(!isExpanded)}>
        <Divider className="expand-divider" styles={{ root: { margin: 0 }, content: { margin: '0 8px' } }}>
          {isExpanded ? <UpOutlined className="expand-icon" /> : <DownOutlined className="expand-icon" />}
        </Divider>
      </div>

      {isExpanded && <Row gutter={[16, 16]} style={{ marginTop: isMobile ? 16 : 24 }}>{renderStatistics(EXPANDED_STATISTICS)}</Row>}
    </div>
  );
};
