import { Table, Tooltip } from 'antd';
import React, { useState, useEffect } from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { colorFromValue, formatPrice } from '@/utils';
import './index.less';

export type OperationListProps = {
  data: API.StockData;
  showAll: boolean;
  showConv: boolean;
};

export const OperationList: React.FC<OperationListProps> = (props) => {
  // 维护展开行的状态
  const [expandedRowKeys, setExpandedRowKeys] = useState<readonly React.Key[]>([]);
  const isMobile = useIsMobile();

  /**
   * 判断某行是否应该被隐藏
   */
  const shouldHideRow = (record: API.Stock): boolean => {
    const shouldHideZeroValue = record.totalValue < 0.1 && !props.showAll;
    const shouldHideConvertible = record.stockType === 'CONV' && !props.showConv;
    return shouldHideZeroValue || shouldHideConvertible;
  };

  /**
   * 根据筛选条件决定行是否隐藏
   */
  const rowClassName = (record: API.Stock): string => {
    return shouldHideRow(record) ? 'hide' : '';
  };

  /**
   * 当筛选条件变化时,折叠需要隐藏的行
   */
  useEffect(() => {
    if (expandedRowKeys.length === 0) return;

    const newExpandedKeys = expandedRowKeys.filter((key) => {
      const stock = props.data.stocks?.find((item) => item.code === key);
      return stock ? !shouldHideRow(stock) : false;
    });

    if (newExpandedKeys.length !== expandedRowKeys.length) {
      setExpandedRowKeys(newExpandedKeys);
    }
  }, [props.showAll, props.showConv, props.data.stocks, expandedRowKeys]);

  /**
   * 操作类型映射
   */
  const operationTypeMap: Record<string, string> = {
    BUY: '买入',
    SELL: '卖出',
    DV: '除权除息',
  };

  /**
   * 操作记录列定义
   */
  const columnsOperation: ColumnsType<API.Operation> = [
    {
      title: '交易日期',
      dataIndex: 'date',
    },
    {
      title: '类型',
      dataIndex: 'type',
      render: (item: string) => <div>{operationTypeMap[item] || item}</div>,
    },
    {
      title: '成交价',
      dataIndex: 'price',
      render: (item: number) => <div>{formatPrice(item)}</div>,
    },
    {
      title: '数量',
      dataIndex: 'count',
    },
    {
      title: '佣金',
      dataIndex: 'fee',
      render: (item: number) => <div>{item?.toFixed(2)}</div>,
    },
    {
      title: '成交金额',
      dataIndex: 'sum',
      render: (item: number) => <div>{item?.toFixed(2)}</div>,
    },
    {
      title: '说明',
      dataIndex: 'comment',
    },
  ];

  /**
   * 展开行渲染函数（显示操作记录明细）
   */
  const expandedRowRender = (record: API.Stock) => (
    <Table
      className="expanded-row-table"
      columns={columnsOperation}
      size="small"
      bordered
      tableLayout="auto"
      dataSource={record.operationList}
      pagination={false}
      scroll={isMobile ? { x: 'max-content' } : undefined}
    />
  );

  /**
   * 股票列表列定义
   * 移动端使用自适应布局，通过 CSS 控制样式
   */
  const columns: ColumnsType<API.Stock> = React.useMemo(() => {
    return [
      {
        title: '名称',
        dataIndex: 'name',
        fixed: isMobile ? false : 'left',
        render: (_: string, record: API.Stock) => (
          <Tooltip title={record.code}>
            <a
              className="stock-name-link"
              target="_blank"
              href={`https://xueqiu.com/S/${record.code}`}
              rel="noreferrer"
            >
              {record.name}
            </a>
          </Tooltip>
        ),
      },
    {
      title: '现价',
      dataIndex: 'priceNow',
      render: (item: string) => <div>{formatPrice(item)}</div>,
    },
    {
      title: '涨跌',
      dataIndex: 'offsetTodayRatio',
      render: (_: string, record: API.Stock) => (
        <div style={{ color: colorFromValue(record.offsetToday) }}>
          {`${record.offsetToday.toFixed(3)} (${record.offsetTodayRatio})`}
        </div>
      ),
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      defaultSortOrder: 'descend',
      sorter: (a: API.Stock, b: API.Stock) => a.totalValue - b.totalValue,
      render: (_: number, record: API.Stock) => {
        const ratio = `${((record.totalValue / props.data.overall.totalValue) * 100).toFixed(2)}%`;
        return (
          <Tooltip title={ratio}>
            <div>{record.totalValue.toFixed(2)}</div>
          </Tooltip>
        );
      },
    },
    {
      title: '持仓',
      dataIndex: 'holdCount',
      render: (_: number, record: API.Stock) => (
        <Tooltip title={`持股 ${record.holdingDuration} 天`}>
          <div>{record.holdCount}</div>
        </Tooltip>
      ),
    },
    {
      title: '摊薄成本/持仓成本',
      dataIndex: 'overallCost',
      render: (_: number, record: API.Stock) => (
        <div>{`${record.overallCost.toFixed(2)}/${record.holdCost.toFixed(2)}`}</div>
      ),
    },
    {
      title: '浮动盈亏',
      dataIndex: 'offsetCurrent',
      sorter: (a: API.Stock, b: API.Stock) => a.offsetCurrent - b.offsetCurrent,
      render: (_: number, record: API.Stock) => {
        const totalOffsetToday = record.offsetToday * record.holdCount;
        return (
          <Tooltip title={totalOffsetToday.toFixed(2)} color={colorFromValue(totalOffsetToday)}>
            <div style={{ color: colorFromValue(record.offsetCurrent) }}>
              {record.offsetCurrent.toFixed(2)}
            </div>
          </Tooltip>
        );
      },
    },
      {
        title: '累计盈亏',
        dataIndex: 'offsetTotal',
        sorter: (a: API.Stock, b: API.Stock) => a.offsetTotal - b.offsetTotal,
        render: (item: number) => (
          <div style={{ color: colorFromValue(item) }}>{item?.toFixed(2)}</div>
        ),
      },
    ];
  }, [isMobile]);

  return (
    <div className="operation-list-wrapper">
      <Table
        rowKey="code"
        columns={columns}
        dataSource={props.data.stocks}
        bordered
        pagination={false}
        rowClassName={rowClassName}
        expandable={{
          expandedRowRender,
          expandedRowKeys,
          onExpandedRowsChange: (keys) => setExpandedRowKeys(keys),
        }}
        scroll={isMobile ? { x: 'max-content' } : undefined}
        size={isMobile ? 'small' : 'middle'}
        tableLayout="auto"
      />
    </div>
  );
};
