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
    xirrAnnualized: number;
    hkdCnyRate?: number;
  };

  type CashFlowRecord = {
    date: string;
    amount: number;
  };

  type Stock = {
    code: string;
    name: string;
    priceNow: number;
    offsetToday: number;
    offsetTodayRatio: number;
    holdCount: number;
    holdCost: number;
    overallCost: number;
    totalValue: number;
    totalValueYesterday: number;
    offsetCurrent: number;
    offsetCurrentRatio: number;
    offsetTotal: number;
    moneyWeightedReturn: number;
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
    /** 港股通人民币成交金额；非港股可为空 */
    amount?: number | null;
    comment: string;
    cash: number;
    stock: number;
    reserve: number;
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
    priceNow: number | null;
    offsetToday: number;
    offsetTodayRatio: number;
    histHigh: number | null;
    pb: number | null;
    pe: number | null;
    risk: string;
    opportunity: string;
    leftPoint: number | null;
    trendPoint: number | null;
    bloodPoint: number | null;
    hidden: boolean;
  };

  type WatchlistResult = BaseResult & {
    data?: WatchItem[];
  };

  type TradingTimeStatus = {
    market: 'cn' | 'hk';
    isTrading: boolean;
    message: string;
  };

  type TradingStatusResult = BaseResult & {
    data?: TradingTimeStatus[];
  };
}