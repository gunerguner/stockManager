import { Table } from 'antd';
import React, { useState, useEffect } from 'react';

import { ColumnsType } from 'antd/lib/table';

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

export const CostList: React.FC<CostListProps> = (props: CostListProps) => {
  const [costList, setCostList] = useState([] as CostListModel[]);

  useEffect(() => {
    initializeCost();
  }, []);

  const initializeCost = () => {
    var costs: CostListModel[] = [];

    for (const stock of props.data) {
      //每一个股票
      for (const operation of stock.operationList) {
        //每一个操作
        if (operation.type == 'DV') continue;

        const year = operation.date.substr(0, 4);
        const month = operation.date.substr(5, 2);

        var yearMap = costs.find((value: CostListModel) => value.id == year);

        if (!!!yearMap) {
          yearMap = { id: year, normalTradeCount: 0, convTradeCount: 0, fee: 0, subList: [] };
          costs.push(yearMap);
        }

        var monthMap = yearMap.subList?.find((value: CostListModel) => value.id == month);

        if (!!!monthMap) {
          monthMap = { id: month, normalTradeCount: 0, convTradeCount: 0, fee: 0 };
          yearMap.subList?.push(monthMap);
        }

        stock.stockType == 'CONV' ? monthMap.convTradeCount++ : monthMap.normalTradeCount++;
        monthMap.fee += operation.fee;

        stock.stockType == 'CONV' ? yearMap.convTradeCount++ : yearMap.normalTradeCount++;
        yearMap.fee += operation.fee;
      }
    }

    costs.sort((a: CostListModel, b: CostListModel) => Number(a.id) - Number(b.id));
    for (const yearMap of costs) {
      yearMap.subList?.sort((a: CostListModel, b: CostListModel) => Number(a.id) - Number(b.id));
    }

    setCostList(costs);
  };

  const Column: ColumnsType<CostListModel> = [
    {
      title: '年份',
      dataIndex: 'id',
      render: (item: number) => {
        return <div style={{ fontWeight: 'bold' }}>{item}</div>;
      },
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
      render: (item: number) => {
        return <div>{item?.toFixed(2)}</div>;
      },
    },
  ];

  const expandedRowRender = (record: CostListModel) => {
    return (
      <Table
        style={{ marginTop: '10px', marginBottom: '10px' }}
        columns={Column}
        bordered
        size="small"
        tableLayout="fixed"
        dataSource={record.subList}
        pagination={false}
        showHeader={false}
      ></Table>
    );
  };

  return (
    <Table
      rowKey="id"
      columns={Column}
      dataSource={costList}
      bordered
      pagination={false}
      expandable={{ expandedRowRender }}
    />
  );
};
