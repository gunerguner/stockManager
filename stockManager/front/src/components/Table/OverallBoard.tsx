import { Table, Row, Col, Input, Form, App } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { updateOriginCash, updateIncomeCash } from '@/services/api';
import { colorFromValue } from '@/utils';

export type OverallBoardProps = {
  data: API.Overall;
  completion?: (success: boolean) => void;
};

export const OverallBoard: React.FC<OverallBoardProps> = (props) => {
  const [form] = Form.useForm();
  const { modal } = App.useApp();

  const columnsOverall: ColumnsType<API.Overall> = [
    {
      title: '当日盈亏',
      dataIndex: 'offsetToday',
      render: (item: number) => {
        return (
          <div style={{ color: colorFromValue(item), fontWeight: 'bold' }}>{item?.toFixed(2)}</div>
        );
      },
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      render: (item: number) => {
        return <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      render: (item: number) => {
        return <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      render: (item: number) => {
        return <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '现金',
      dataIndex: 'totalCash',
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '其它现金收入',
      dataIndex: 'incomeCash',
      render: (item: number) => {
        return (
          <Row>
            <Col span={15}>
              <div>{item?.toFixed(2)}</div>
            </Col>
            <Col>
              <a
                onClick={() => {
                  modal.confirm({
                    title: '编辑现金收入',
                    content: (
                      <Form
                        style={{ marginTop: '30px' }}
                        form={form}
                        layout="vertical"
                        name="incomeCash"
                      >
                        <Form.Item
                          name="incomeCash"
                          rules={[{ required: true, message: '请输入现金收入' }]}
                        >
                          <Input type="number" defaultValue={item} />
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
                }}
              >
                编辑
              </a>
            </Col>
          </Row>
        );
      },
    },
    {
      title: '本金',
      dataIndex: 'originCash',
      render: (item: number) => {
        return (
          <Row>
            <Col span={15}>
              <div>{item?.toFixed(2)}</div>
            </Col>
            <Col>
              <a
                onClick={() => {
                  modal.confirm({
                    title: '编辑本金',
                    content: (
                      <Form
                        style={{ marginTop: '30px' }}
                        form={form}
                        layout="vertical"
                        name="originCash"
                      >
                        <Form.Item name="cash" rules={[{ required: true, message: '请输入本金' }]}>
                          <Input type="number" defaultValue={item} />
                        </Form.Item>
                      </Form>
                    ),
                    onOk: async () => {
                      const { cash } = await form.validateFields();
                      const response = await updateOriginCash(cash);
                      if (props.completion) {
                        props.completion(response.status === 1);
                      }
                    },
                  });
                }}
              >
                编辑
              </a>
            </Col>
          </Row>
        );
      },
    },
    {
      title: '总资产',
      dataIndex: 'totalAsset',
      render: (item: number) => {
        return <div style={{ fontWeight: 'bold' }}>{item?.toFixed(2)}</div>;
      },
    },
  ];

  return (
    <Table 
      columns={columnsOverall} 
      dataSource={[props.data]} 
      bordered 
      pagination={false}
      rowKey={() => 'overall'}
    />
  );
};
