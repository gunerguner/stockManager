import { Statistic, Row, Col, Input, Form, App, Divider } from 'antd';
import React, { useState } from 'react';
import { UpOutlined, DownOutlined } from '@ant-design/icons';
import { updateIncomeCash } from '@/services/api';
import { colorFromValue } from '@/utils';
import { useIsMobile } from '@/hooks/useIsMobile';
import './index.less';

export type OverallBoardProps = {
  data: API.Overall;
  completion?: (success: boolean) => void;
};

export const OverallBoard: React.FC<OverallBoardProps> = (props) => {
  const [form] = Form.useForm();
  const { modal } = App.useApp();
  const isMobile = useIsMobile();
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
          props.completion(response.status === 1);
        }
      },
    });
  };

  // 每行显示的列数（移动端2列，桌面端4列）
  const colSpan = isMobile ? 12 : 6;

  /**
   * 切换展开/折叠状态
   */
  const toggleExpand = (): void => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="overall-board-wrapper">
      <Row gutter={[16, 16]}>
        {/* 当日盈亏 - 放在最前面 */}
        <Col span={colSpan}>
          <Statistic
            title="当日盈亏"
            value={data.offsetToday || 0}
            precision={2}
            className="main-statistic"
            valueStyle={{
              color: colorFromValue(data.offsetToday || 0),
              fontWeight: 'bold',
            }}
          />
        </Col>

        {/* 总资产 - 放在最前面 */}
        <Col span={colSpan}>
          <Statistic
            title="总资产"
            value={data.totalAsset || 0}
            precision={2}
            className="main-statistic"
            valueStyle={{ fontWeight: 'bold' }}
          />
        </Col>
      </Row>

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
          {/* 浮动盈亏 */}
          <Col span={colSpan}>
            <Statistic
              title="浮动盈亏"
              value={data.offsetCurrent || 0}
              precision={2}
              valueStyle={{ color: colorFromValue(data.offsetCurrent || 0) }}
            />
          </Col>

          {/* 累计盈亏 */}
          <Col span={colSpan}>
            <Statistic
              title="累计盈亏"
              value={data.offsetTotal || 0}
              precision={2}
              valueStyle={{ color: colorFromValue(data.offsetTotal || 0) }}
            />
          </Col>

          {/* 市值 */}
          <Col span={colSpan}>
            <Statistic
              title="市值"
              value={data.totalValue || 0}
              precision={2}
              valueStyle={{ color: colorFromValue(data.totalValue || 0) }}
            />
          </Col>

          {/* 现金 */}
          <Col span={colSpan}>
            <Statistic title="现金" value={data.totalCash || 0} precision={2} />
          </Col>

          {/* 其它现金收入 - 带编辑按钮 */}
          <Col span={colSpan}>
            <Statistic
              title="其它现金收入"
              value={data.incomeCash || 0}
              precision={2}
              suffix={
                <a
                  onClick={handleEditIncomeCash}
                  style={{ fontSize: '12px', marginLeft: '8px' }}
                >
                  编辑
                </a>
              }
            />
          </Col>

          {/* 本金 */}
          <Col span={colSpan}>
            <Statistic title="本金" value={data.originCash || 0} precision={2} />
          </Col>
        </Row>
      )}
    </div>
  );
};
