// @ts-ignore
/* eslint-disable */

declare namespace API {
  type UserResult = {
    status?: number;
    info?: CurrentUser;
  }

  type CurrentUser = {
    name?: string;
    avatar?: string;
    userid?: string;
    email?: string;
    signature?: string;
    title?: string;
    group?: string;
    tags?: { key?: string; label?: string }[];
    notifyCount?: number;
    unreadCount?: number;
    country?: string;
    access?: string;
    geographic?: {
      province?: { label?: string; key?: string };
      city?: { label?: string; key?: string };
    };
    address?: string;
    phone?: string;
  };

  type LoginResult = {
    status?: number;
    currentAuthority?: string;
  };

  type LoginParams = {
    username?: string;
    password?: string;
    autoLogin?: boolean;
  };

  type ErrorResponse = {
    /** 业务约定的错误码 */
    errorCode: string;
    /** 业务上的错误信息 */
    errorMessage?: string;
    /** 业务上的请求是否成功 */
    success?: boolean;
  };

  type StockResult = {
    status?: number;
    data?: StockData;
  };

  type StockData = {
    stocks: Stock[];
    overall: Overall;
  }

  type Overall = {
    offsetCurrent: number,
    offsetTotal: number,
    totalValue: number,
    offsetCurrentRatio: string,
    offsetToday: number,
    totalCash: number,
    originCash: number,
  }

  type Stock = {
    code: string,
    name: string,
    priceNow: string,
    offsetToday: number,
    offsetTodayRatio: string,
    holdCount: number,
    holdCost: number,
    overallCost: number,
    totalValue: number,
    totalValueYesterday: number,
    offsetCurrent: number,
    offsetCurrentRatio: string,
    offsetTotal:number,
    operationList: Operation[],
    totalOffsetToday: number
  }

  type Operation = {
    date: string,
    type: string,
    price: number,
    count: number,
    fee: number,
    sum: number,
    comment: string,
  }

}
