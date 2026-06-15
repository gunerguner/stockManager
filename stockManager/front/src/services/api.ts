// @ts-ignore
/* eslint-disable */
import { request } from '@umijs/max';
import type { RequestOptions } from '@umijs/max';

const API_BASE_URL = '';

// 通用JSON请求头
const JSON_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * 统一的GET请求封装
 */
const getRequest = <T>(endpoint: string, options?: RequestOptions) => {
  return request<T>(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    credentials: 'include', // 确保发送 Cookie（包括 CSRF token）
    ...options,
  });
};

/**
 * 统一的POST请求封装
 */
function postRequest<T>(endpoint: string, options?: RequestOptions): Promise<T>;
function postRequest<T>(
  endpoint: string,
  data: Record<string, unknown>,
  options?: RequestOptions,
): Promise<T>;
function postRequest<T>(
  endpoint: string,
  arg2?: Record<string, unknown> | RequestOptions,
  arg3?: RequestOptions,
): Promise<T> {
  const data = arg3 !== undefined ? (arg2 as Record<string, unknown>) : undefined;
  const options = arg3 !== undefined ? arg3 : (arg2 as RequestOptions | undefined);

  return request<T>(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: JSON_HEADERS,
    credentials: 'include', // 确保发送 Cookie（包括 CSRF token）
    data,
    ...options,
  });
}

/** 获取当前用户信息 GET /api/currentUser */
export async function getCurrentUser(options?: RequestOptions) {
  return getRequest<API.UserResult>('/api/currentUser', options);
}

/** 用户登录 POST /api/login */
export async function login(params: API.LoginParams, options?: RequestOptions) {
  return postRequest<API.LoginResult>('/api/login', params, options);
}

/** 用户登出 POST /api/logout */
export async function logout(options?: RequestOptions) {
  return postRequest<Record<string, unknown>>('/api/logout', options);
}

/** 获取操作列表 GET /api/operations */
export async function getOperations(options?: RequestOptions) {
  return getRequest<API.OperationsResult>('/api/operations', options);
}

/** 获取股票计算结果 GET /api/stocks */
export async function getStocks(options?: RequestOptions) {
  return getRequest<API.StockResult>('/api/stocks', options);
}

/** 更新收益资金 POST /api/updateIncomeCash */
export async function updateIncomeCash(incomeCash: number, options?: RequestOptions) {
  return postRequest<API.BaseResult>('/api/updateIncomeCash', { incomeCash }, options);
}

/** 更新分红 POST /api/dividend */
export async function updateDividend(options?: RequestOptions) {
  return postRequest<API.DividendResult>('/api/dividend', options);
}

/** 清理 Redis 缓存 POST /api/clearCache */
export async function clearCache(options?: RequestOptions) {
  return postRequest<API.ClearCacheResult>('/api/clearCache', options);
}

/** 获取关注列表 GET /api/watchlist */
export async function getWatchlist(options?: RequestOptions) {
  return getRequest<API.WatchlistResult>('/api/watchlist', options);
}