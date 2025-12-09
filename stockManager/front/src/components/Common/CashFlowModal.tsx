import { App, Table, Typography } from 'antd';
import React from 'react';
import type { ColumnsType } from 'antd/lib/table';
import { useIsMobile } from '@/hooks/useIsMobile';
import { renderAmount } from '@/utils/renderTool';
import './index.less';

const { Text } = Typography;

// ==================== 类型定义 ====================

export type ShowCashFlowParams = {
  totalCashIn: number;
  cashFlowList: API.CashFlowRecord[];
};

// ==================== 渲染函数 ====================

/** 渲染浮层内容 */
const renderCashFlowContent = (params: ShowCashFlowParams, isMobile: boolean): React.ReactNode => {
  const { totalCashIn, cashFlowList } = params;

  if (!cashFlowList?.length) {
    return <div className="empty-data">暂无出入金记录</div>;
  }

  const columns: ColumnsType<API.CashFlowRecord> = [
    {
      title: '交易日期',
      dataIndex: 'date',
      width: isMobile ? 100 : 120,
    },
    {
      title: '出入金',
      dataIndex: 'amount',
      width: isMobile ? 100 : 150,
      render: (value: number) => {
        const isInflow = value > 0;
        return renderAmount(value, isInflow ? 'red' : 'green');
      },
    },
  ];

  return (
    <div className="cash-flow-content">
      <div className="stock-group-header">
        <div className="stock-header-left">
          <Text>净入金：</Text>
          {renderAmount(totalCashIn)}
        </div>
      </div>
      <Table
        className="cash-flow-table"
        columns={columns}
        dataSource={cashFlowList}
        rowKey={(record, index) => `${record.date}-${index}`}
        size="small"
        bordered
        pagination={false}
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
};

// ==================== Hook ====================

export const useCashFlowModal = () => {
  const { modal } = App.useApp();
  const isMobile = useIsMobile();

  const showCashFlow = React.useCallback(
    (params: ShowCashFlowParams) => {
      modal.info({
        title: '出入金明细',
        content: renderCashFlowContent(params, isMobile),
        width: isMobile ? '95%' : 600,
        className: 'cash-flow-modal',
        icon: null,
        footer: null,
        closable: true,
        maskClosable: true,
      });
    },
    [modal, isMobile],
  );

  return { showCashFlow };
};

