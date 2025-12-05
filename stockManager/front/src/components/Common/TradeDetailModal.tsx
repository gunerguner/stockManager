import { Table, Typography, Space, Divider, App } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { formatPrice, renderAmount } from '@/utils/renderTool';
import './index.less';

const { Text, Link } = Typography;

// ==================== 类型定义 ====================

export type TradeDetailDisplayType = 'stockInfo' | 'tradeList';

export type ShowTradeDetailParams = {
  data: Array<{ stock: API.Stock; operations: API.Operation[] }>;
  title?: string;
  displayType: TradeDetailDisplayType;
};

// ==================== 常量 ====================

const OPERATION_TYPE_MAP: Record<string, string> = {
  BUY: '买入',
  SELL: '卖出',
  DV: '除权除息',
};

// ==================== 表格列配置 ====================

const getColumnsOperation = (isMobile: boolean): ColumnsType<API.Operation> => [
  { title: '交易日期', dataIndex: 'date', width: isMobile ? 90 : 110 },
  {
    title: '类型',
    dataIndex: 'type',
    width: isMobile ? 60 : 80,
    render: (v: string) => <div>{OPERATION_TYPE_MAP[v] || v}</div>,
  },
  {
    title: '成交价',
    dataIndex: 'price',
    width: isMobile ? 70 : 90,
    render: (v: number) => <div>{formatPrice(v)}</div>,
  },
  { title: '数量', dataIndex: 'count', width: isMobile ? 60 : 80 },
  {
    title: '佣金',
    dataIndex: 'fee',
    width: isMobile ? 60 : 80,
    render: (v: number) => <div>{v?.toFixed(2)}</div>,
  },
  {
    title: '成交金额',
    dataIndex: 'sum',
    width: isMobile ? 80 : 100,
    render: (v: number) => <div>{v?.toFixed(2)}</div>,
  },
  { title: '说明', dataIndex: 'comment', width: isMobile ? 100 : 150 },
];

// ==================== 渲染函数 ====================

/** 渲染股票信息（PC端） */
const renderStockInfoPC = (stock: API.Stock) => (
  <>
    <Divider type="vertical" />
    <Text>现价：{formatPrice(stock.priceNow)}</Text>
    <Text>持股：{stock.holdCount}</Text>
    <Text>累计盈亏：{renderAmount(stock.offsetTotal)}</Text>
  </>
);

/** 渲染股票信息（移动端） */
const renderStockInfoMobile = (stock: API.Stock) => (
  <div className="stock-info-row">
    <Space size="small" wrap>
      <Text>现价：{formatPrice(stock.priceNow)}</Text>
      <Text>持股：{stock.holdCount}</Text>
      <Text>累计盈亏：{renderAmount(stock.offsetTotal)}</Text>
    </Space>
  </div>
);

/** 渲染交易列表内容 */
const renderTradeListContent = (
  data: ShowTradeDetailParams['data'],
  isMobile: boolean,
  displayType: TradeDetailDisplayType
): React.ReactNode => {
  if (data.length === 0) {
    return <div className="empty-data">暂无交易数据</div>;
  }

  return (
    <div className="trade-detail-content">
      {data.map((group, index) => {
        const showStockInfo = displayType === 'stockInfo' && index === 0;

        return (
          <div key={group.stock.code} className="trade-group-item">
            <div className="stock-group-header">
              <div className="stock-header-left">
                <Space wrap>
                  <Link
                    href={`https://xueqiu.com/S/${group.stock.code}`}
                    target="_blank"
                    rel="noreferrer"
                    strong
                    className="stock-group-link"
                  >
                    {group.stock.name}
                  </Link>
                  <Text type="secondary">({group.stock.code})</Text>
                  {showStockInfo && !isMobile && renderStockInfoPC(group.stock)}
                </Space>
                {showStockInfo && isMobile && renderStockInfoMobile(group.stock)}
              </div>
              <Text type="secondary" className="trade-count">
                共 {group.operations.length} 笔交易
              </Text>
            </div>
            <Table
              className="trade-detail-table"
              columns={getColumnsOperation(isMobile)}
              dataSource={group.operations}
              rowKey={(record, idx) => `${group.stock.code}-${record.date}-${idx}`}
              size="small"
              bordered
              pagination={false}
              scroll={{ x: 'max-content' }}
            />
            {index < data.length - 1 && <Divider style={{ margin: '24px 0' }} />}
          </div>
        );
      })}
    </div>
  );
};

// ==================== Hook ====================

export const useTradeDetailModal = () => {
  const { modal } = App.useApp();
  const isMobile = useIsMobile();

  const showTradeDetail = React.useCallback(
    (params: ShowTradeDetailParams) => {
      const { data, title = '所有交易明细', displayType } = params;

      modal.info({
        title,
        content: renderTradeListContent(data, isMobile, displayType),
        width: isMobile ? '95%' : 1200,
        className: 'trade-detail-modal',
        icon: null,
        footer: null,
        closable: true,
        maskClosable: true,
      });
    },
    [modal, isMobile]
  );

  return { showTradeDetail };
};
