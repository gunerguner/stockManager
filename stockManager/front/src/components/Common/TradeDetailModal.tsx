import { Table, Typography, Space, Divider, App } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { colorFromValue, formatPrice } from '@/utils';
import './index.less';

const { Text, Link } = Typography;

/**
 * 显示内容类型
 */
export type TradeDetailDisplayType = 'stockInfo' | 'tradeList';

/**
 * 显示交易详情 Modal 的参数
 */
export type ShowTradeDetailParams = {
  // 交易数据（统一使用数组格式，单股票也是一个元素的数组）
  data: Array<{
    stock: API.Stock;
    operations: API.Operation[];
  }>;
  // Modal 标题（可选，默认为"所有交易明细"）
  title?: string;
  // 显示内容类型（用于决定是否显示股票信息）
  displayType: TradeDetailDisplayType;
};

/**
 * 操作类型映射
 */
const operationTypeMap: Record<string, string> = {
  BUY: '买入',
  SELL: '卖出',
  DV: '除权除息',
};

/**
 * 操作记录列定义（从 OperationList 复用）
 */
const getColumnsOperation = (isMobile: boolean): ColumnsType<API.Operation> => [
  {
    title: '交易日期',
    dataIndex: 'date',
    width: isMobile ? 90 : 110,
  },
  {
    title: '类型',
    dataIndex: 'type',
    width: isMobile ? 60 : 80,
    render: (item: string) => <div>{operationTypeMap[item] || item}</div>,
  },
  {
    title: '成交价',
    dataIndex: 'price',
    width: isMobile ? 70 : 90,
    render: (item: number) => <div>{item?.toFixed(2)}</div>,
  },
  {
    title: '数量',
    dataIndex: 'count',
    width: isMobile ? 60 : 80,
  },
  {
    title: '佣金',
    dataIndex: 'fee',
    width: isMobile ? 60 : 80,
    render: (item: number) => <div>{item?.toFixed(2)}</div>,
  },
  {
    title: '成交金额',
    dataIndex: 'sum',
    width: isMobile ? 80 : 100,
    render: (item: number) => <div>{item?.toFixed(2)}</div>,
  },
  {
    title: '说明',
    dataIndex: 'comment',
    width: isMobile ? 100 : 150,
  },
];



/**
 * 渲染交易列表内容
 */
const renderTradeListContent = (
  data: Array<{ stock: API.Stock; operations: API.Operation[] }>,
  isMobile: boolean,
  displayType: TradeDetailDisplayType
): React.ReactNode => {
  if (data.length === 0) {
    return <div className="empty-data">暂无交易数据</div>;
  }

  const showStockInfo = displayType === 'stockInfo';

  return (
    <div className="trade-detail-content">
      {data.map((group, index) => {
        const shouldShowStockInfo = showStockInfo && index === 0;
        
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
                  {shouldShowStockInfo && !isMobile && (
                    <>
                      <Divider type="vertical" />
                      <Text>现价：{formatPrice(group.stock.priceNow)}</Text>
                      <Text>持股：{group.stock.holdCount}</Text>
                      <Text>
                        累计盈亏：
                        <span style={{ color: colorFromValue(group.stock.offsetTotal) }}>
                          {group.stock.offsetTotal.toFixed(2)}
                        </span>
                      </Text>
                    </>
                  )}
                </Space>
                {shouldShowStockInfo && isMobile && (
                  <div className="stock-info-row">
                    <Space size="small" wrap>
                      <Text>现价：{formatPrice(group.stock.priceNow)}</Text>
                      <Text>持股：{group.stock.holdCount}</Text>
                      <Text>
                        累计盈亏：
                        <span style={{ color: colorFromValue(group.stock.offsetTotal) }}>
                          {group.stock.offsetTotal.toFixed(2)}
                        </span>
                      </Text>
                    </Space>
                  </div>
                )}
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
            {index < data.length - 1 && (
              <Divider style={{ margin: '24px 0' }} />
            )}
          </div>
        );
      })}
    </div>
  );
};

/**
 * 使用命令式 API 显示交易详情 Modal
 */
export const useTradeDetailModal = () => {
  const { modal } = App.useApp();
  const isMobile = useIsMobile();

  const showTradeDetail = React.useCallback((params: ShowTradeDetailParams) => {
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
  }, [modal, isMobile]);

  return { showTradeDetail };
};

