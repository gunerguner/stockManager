import { App, Space, Table, Tooltip, Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { renderAmount } from '@/utils/renderAmount';
import './index.less';

const { Text } = Typography;

// ==================== 类型定义 ====================

export interface StockProfitData {
  code: string;
  name: string;
  netIncome: number;
}

export type ShowStockProfitParams = {
  data: StockProfitData[];
  categoryName: string;
  profit: number;
  loss: number;
  netIncome: number;
};

// ==================== 渲染函数 ====================

/** 渲染汇总信息 */
const renderSummaryHeader = (
  categoryName: string,
  profit: number,
  loss: number,
  netIncome: number,
  isMobile: boolean,
): React.ReactNode => {
  if (isMobile) {
    return (
      <div className="stock-profit-header">
        <div className="category-name">
          <strong>{categoryName}</strong>
        </div>
        <div className="summary-info-row">
          <Space size="small" wrap>
            <Text>获利：{renderAmount(profit, 'red')}</Text>
            <Text>亏损：{renderAmount(loss, 'green')}</Text>
            <Text>净盈亏：{renderAmount(netIncome)}</Text>
          </Space>
        </div>
      </div>
    );
  }

  return (
    <div className="stock-profit-header">
      <Space size="middle" wrap>
        <strong>{categoryName}</strong>
        <Text>获利：{renderAmount(profit, 'red')}</Text>
        <Text>亏损：{renderAmount(loss, 'green')}</Text>
        <Text>净盈亏：{renderAmount(netIncome)}</Text>
      </Space>
    </div>
  );
};

const renderStockProfitContent = (
  params: ShowStockProfitParams,
  isMobile: boolean,
): React.ReactNode => {
  const { data, categoryName, profit, loss, netIncome } = params;

  if (!data || data.length === 0) {
    return <div className="empty-data">暂无数据</div>;
  }

  // 按净盈亏降序排列
  const sortedData = [...data].sort((a, b) => b.netIncome - a.netIncome);

  const columns: ColumnsType<StockProfitData> = [
    {
      title: '股票名称',
      dataIndex: 'name',
      width: isMobile ? 120 : 200,
      render: (name: string, record: StockProfitData) => (
        <Tooltip title={record.code}>
          <span>{name}</span>
        </Tooltip>
      ),
    },
    {
      title: '净盈亏',
      dataIndex: 'netIncome',
      width: isMobile ? 100 : 150,
      render: (value: number) => renderAmount(value),
    },
  ];

  return (
    <div className="stock-profit-content">
      {renderSummaryHeader(categoryName, profit, loss, netIncome, isMobile)}
      <Table
        className="stock-profit-table"
        columns={columns}
        dataSource={sortedData}
        rowKey="code"
        size="small"
        bordered
        pagination={false}
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
};

// ==================== Hook ====================

export const useStockProfitModal = () => {
  const { modal } = App.useApp();
  const isMobile = useIsMobile();

  const showStockProfit = React.useCallback(
    (params: ShowStockProfitParams) => {
      modal.info({
        title: '盈亏明细',
        content: renderStockProfitContent(params, isMobile),
        width: isMobile ? '95%' : 600,
        className: 'stock-profit-modal',
        icon: null,
        footer: null,
        closable: true,
        maskClosable: true,
      });
    },
    [modal, isMobile],
  );

  return { showStockProfit };
};

