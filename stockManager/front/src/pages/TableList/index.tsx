import { Table, Button, Row, Col, Modal, Input, Form, InputNumber } from 'antd';

import React, { useState, useEffect } from 'react';

import ProCard from '@ant-design/pro-card';

import { history } from 'umi';
import { fetch, updateOriginCash } from '../../services/api';

// import { Columns, ColumnsOverAll, ColumnsOperation } from '../../types/tableList';
import { ColumnsType } from 'antd/lib/table';

import './index.less';

const TableList: React.FC = () => {
  const [overAllData, setOverallData] = useState({} as API.Overall);
  const [stockData, setStockData] = useState([] as API.Stock[]);

  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const ColumnsOverAll: ColumnsType<API.Overall> = [
    {
      title: '当日盈亏',
      dataIndex: 'offsetToday',
      render: (item: number) => {
        const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
        return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      render: (item: number) => {
        const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
        return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      render: (item: number) => {
        const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
        return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      render: (item: number) => {
        const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
        return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
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
      title: '本金',
      dataIndex: 'originCash',
      render: (item: number) => {
        const [form] = Form.useForm();
        return (
          <Row>
            <Col span={15}>
              <div>{item?.toFixed(2)}</div>
            </Col>
            <Col>
              <a
                onClick={() => {
                  Modal.confirm({
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

                      await updateBase(cash);
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
  ];

  const Columns: ColumnsType<API.Stock> = [
    {
      title: '名称',
      dataIndex: 'name',
      render: (value: any, record: API.Stock, index: number) => {
        return (
          <a
            target="_blank"
            href={'https://xueqiu.com/S/' + record.code}
            style={{ textDecoration: 'none', fontWeight: 'bold', fontSize: '13px' }}
          >
            {record.name + ' (' + record.code + ')'}
          </a>
        );
      },
    },
    {
      title: '现价',
      dataIndex: 'priceNow',
    },
    {
      title: '涨跌',
      dataIndex: 'offsetTodayRatio',
      render: (value: any, record: API.Stock, index: number) => {
        const color = record.offsetToday > 0 ? 'red' : record.offsetToday < 0 ? 'green' : 'black';
        return (
          <div style={{ color: color }}>
            {record?.offsetToday.toFixed(3) + ' (' + record?.offsetTodayRatio + ' )'}
          </div>
        );
      },
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      defaultSortOrder: 'descend',
      sorter: (a: API.Stock, b: API.Stock) => {
        return a.totalValue - b.totalValue;
      },
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '持仓',
      dataIndex: 'holdCount',
    },
    {
      title: '摊薄成本/持仓成本',
      dataIndex: 'overallCost',
      render: (value: any, record: API.Stock, index: number) => {
        return <div>{record?.overallCost.toFixed(2) + '/' + record?.holdCost.toFixed(2)}</div>;
      },
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      sorter: (a: API.Stock, b: API.Stock) => {
        return a.offsetCurrent - b.offsetCurrent;
      },
      render: (item: number) => {
        const color = item > 0 ? 'red' : item < 0 ? 'green' : 'black';
        return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '累计盈亏',
      dataIndex: 'offsetTotal',
      sorter: (a: API.Stock, b: API.Stock) => {
        return a.offsetTotal - b.offsetTotal;
      },
      render: (item: number) => {
        const color = item > 0 ? 'red' : 'green';
        return <div style={{ color: color }}>{item?.toFixed(2)}</div>;
      },
    },
  ];

  const ColumnsOperation: ColumnsType<API.Operation> = [
    {
      title: '交易日期',
      dataIndex: 'date',
    },
    {
      title: '类型',
      dataIndex: 'type',
      render: (item: string) => {
        return <div>{item == 'BUY' ? '买入' : item == 'SELL' ? '卖出' : '除权除息'}</div>;
      },
    },
    {
      title: '成交价',
      dataIndex: 'price',
    },
    {
      title: '数量',
      dataIndex: 'count',
    },
    {
      title: '佣金',
      dataIndex: 'fee',
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '成交金额',
      dataIndex: 'sum',
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
    {
      title: '说明',
      dataIndex: 'comment',
    },
  ];

  const fetchData = async () => {
    const response = await fetch();
    if (response.status == 1 && !!response.data) {
      setOverallData(response.data?.overall);
      setStockData(response.data?.stocks);
    } else if (response.status == 302) {
      history.push('/login');
    }
  };

  const updateBase = async (cash: number) => {
    const response = await updateOriginCash(cash);
    if (response.status == 1 ) {
      fetchData();
    } else if (response.status == 302) {
      history.push('/login');
    }
  };

  const rowClassName = (record: API.Stock, index: number): string => {
    return record.totalValue < 0.1 && !showAll ? 'hide' : '';
  };

  const expandedRowRender = (record: API.Stock) => {
    return (
      <Table
        style={{ marginTop: '10px', marginBottom: '10px' }}
        columns={ColumnsOperation}
        size="small"
        bordered
        tableLayout="fixed"
        dataSource={record.operationList}
        pagination={false}
      ></Table>
    );
  };

  return (
    <ProCard direction="column" ghost gutter={[0, 8]}>
      <ProCard colSpan={24}>
        <Table columns={ColumnsOverAll} dataSource={[overAllData]} bordered pagination={false} />
      </ProCard>
      <ProCard colSpan={24}>
        <Row>
          <Col offset={20} span={6}>
            <Button type="primary" onClick={() => setShowAll(!showAll)}>
              {(showAll ? '隐藏' : '显示') + '市值为零的股票'}
            </Button>
          </Col>
        </Row>
        <Row style={{ marginTop: '20px' }}>
          <Col span={24}>
            <Table
              rowKey="code"
              columns={Columns}
              dataSource={stockData}
              bordered
              pagination={false}
              rowClassName={rowClassName}
              expandable={{ expandedRowRender }}
            />
          </Col>
        </Row>
      </ProCard>
    </ProCard>
  );
};

export default TableList;
