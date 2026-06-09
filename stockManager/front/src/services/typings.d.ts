// @ts-ignore
/* eslint-disable */

declare namespace API {

  // 基础响应结构
  type BaseResult = {
    status: number;
    message?: string;
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
    username: string;
    password: string;
    autoLogin?: boolean;
  };

  type OperationsResult = BaseResult & {
    data?: Record<string, Operation[]>;
  };

  type StockResult = BaseResult & {
    data?: StockData;
  };

  type StockData = {
    stocks: Stock[];
    overall: Overall;
    markets?: MarketsMetadata;
  };

  type MarketStatus = {
    inTradingHours: boolean;
    priceUpdatedAt?: string | null;
  };

  type MarketsMetadata = {
    cn?: MarketStatus;
    hk?: MarketStatus;
  };

  type Overall = {
    offsetCurrent: number;
    offsetTotal: number;
    totalValue: number;
    offsetToday: number;
    totalCash: number;
    incomeCash: number;
    originCash: number;
    totalAsset: number;
    totalCost: number;
    cashFlowList: CashFlowRecord[];
    xirrAnnualized: string;
    hkdCnyRate?: number;
  };

  type CashFlowRecord = {
    date: string;
    amount: number;
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
    moneyWeightedReturn: string;
    totalOffsetToday: number;
    isNew: boolean;
    stockType: string;
    holdingDuration: number;
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

  type DividendResult = BaseResult & {
    data?: DividendUpdate[];
  };

  type DividendUpdate = {
    code: string;
    name: string;
  };

  type ClearCacheResult = BaseResult & {
    data?: { deletedCount: number };
  };

  type WatchItem = {
    code: string;
    name: string;
    holding: boolean;
    priceNow: number | null;
    histHigh: number | null;
    pb: number | null;
    pe: number | null;
    risk: string;
    opportunity: string;
    leftPoint: number | null;
    trendPoint: number | null;
    bloodPoint: number | null;
  };

  type WatchlistResult = BaseResult & {
    data?: WatchItem[];
  };
}