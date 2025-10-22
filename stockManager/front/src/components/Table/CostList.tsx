import { Table } from 'antd';
import React, { useState, useEffect } from 'react';
import type { ColumnsType } from 'antd/lib/table';

interface CostListModel {
  id: string;
  normalTradeCount: number;
  convTradeCount: number;
  fee: number;
  subList?: CostListModel[];
}

export type CostListProps = {
  data: API.Stock[];
};

export const CostList: React.FC<CostListProps> = (props) => {
  const [costList, setCostList] = useState<CostListModel[]>([]);

  /**
   * 初始化成本统计数据
   * 统计每年每月的交易次数和费用
   */
  const initializeCost = React.useCallback(() => {
    const costs: CostListModel[] = [];

    // 遍历所有股票
    for (const stock of props.data) {
      // 遍历每个股票的操作记录
      for (const operation of stock.operationList) {
        // 跳过分红操作
        if (operation.type === 'DV') continue;

        const year = operation.date.substring(0, 4);
        const month = operation.date.substring(5, 7);

        // 查找或创建年份记录
        let yearMap = costs.find((value) => value.id === year);

        if (!yearMap) {
          yearMap = { id: year, normalTradeCount: 0, convTradeCount: 0, fee: 0, subList: [] };
          costs.push(yearMap);
        }

        // 查找或创建月份记录
        let monthMap = yearMap.subList?.find((value) => value.id === month);

        if (!monthMap) {
          monthMap = { id: month, normalTradeCount: 0, convTradeCount: 0, fee: 0 };
          yearMap.subList?.push(monthMap);
        }

        // 统计交易次数和费用
        const isConvertible = stock.stockType === 'CONV';
        
        if (isConvertible) {
          monthMap.convTradeCount++;
          yearMap.convTradeCount++;
        } else {
          monthMap.normalTradeCount++;
          yearMap.normalTradeCount++;
        }

        monthMap.fee += operation.fee;
        yearMap.fee += operation.fee;
      }
    }

    // 按时间排序
    costs.sort((a, b) => Number(a.id) - Number(b.id));
    for (const yearItem of costs) {
      yearItem.subList?.sort((a, b) => Number(a.id) - Number(b.id));
    }

    setCostList(costs);
  }, [props.data]);

  useEffect(() => {
    initializeCost();
  }, [initializeCost]);

  const columns: ColumnsType<CostListModel> = [
    {
      title: '年份',
      dataIndex: 'id',
      render: (item: string) => <strong>{item}</strong>,
    },
    {
      title: '普通交易次数',
      dataIndex: 'normalTradeCount',
    },
    {
      title: '可转债交易次数',
      dataIndex: 'convTradeCount',
    },
    {
      title: '费用',
      dataIndex: 'fee',
      render: (item: number) => <div>{item?.toFixed(2)}</div>,
    },
  ];

  /**
   * 展开行渲染函数（显示月份明细）
   */
  const expandedRowRender = (record: CostListModel) => (
    <Table
      style={{ margin: '10px 0' }}
      columns={columns}
      bordered
      size="small"
      tableLayout="fixed"
      dataSource={record.subList}
      pagination={false}
      showHeader={false}
    />
  );

  return (
    <Table
      rowKey="id"
      columns={columns}
      dataSource={costList}
      bordered
      pagination={false}
      expandable={{ expandedRowRender }}
    />
  );
};
