// @ts-ignore
/* eslint-disable */

declare namespace API {
  type BaseResult = {
    status?: number;
  };

  type UserResult = BaseResult & {
    info?: CurrentUser;
  };

  type CurrentUser = {
    name: string;
    avatar?: string;
    username?: string;
    access?: string;
  };

  type LoginResult = BaseResult & {
    currentAuthority?: string;
  };

  type LoginParams = {
    username?: string;
    password?: string;
    autoLogin?: boolean;
  };

  type StockResult = BaseResult & {
    data?: StockData;
  };

  type StockData = {
    stocks: Stock[];
    overall: Overall;
  };

  type Overall = {
    offsetCurrent: number;
    offsetTotal: number;
    totalValue: number;
    offsetCurrentRatio: string;
    offsetToday: number;
    totalCash: number;
    incomeCash: number;
    originCash: number;
    totalAsset: number;
  };

  type Stock = {
    code: string;
    name: string;
    priceNow: string;
    offsetToday: number;
    offsetTodayRatio: string;
    holdCount: number;
    holdCost: number;
    overallCost: number;
    totalValue: number;
    totalValueYesterday: number;
    offsetCurrent: number;
    offsetCurrentRatio: string;
    offsetTotal: number;
    operationList: Operation[];
    totalOffsetToday: number;
    isNew:boolean;
    stockType: string;
  };

  type Operation = {
    date: string;
    type: string;
    price: number;
    count: number;
    fee: number;
    sum: number;
    comment: string;
  };

  type DividentResult = BaseResult & {
    data?: string[];
  };
}
