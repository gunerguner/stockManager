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
const postRequest = <T>(endpoint: string, data?: Record<string, unknown>, options?: RequestOptions) => {
  return request<T>(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: JSON_HEADERS,
    credentials: 'include', // 确保发送 Cookie（包括 CSRF token）
    data,
    ...options,
  });
};

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
  return postRequest<Record<string, unknown>>('/api/logout', undefined, options);
}

/** 获取股票数据 GET /api/ */
export async function getStockList(options?: RequestOptions) {
  return getRequest<API.StockResult>('/api/', options);
}

/** 更新收益资金 POST /api/updateIncomeCash */
export async function updateIncomeCash(incomeCash: number, options?: RequestOptions) {
  return postRequest<API.BaseResult>('/api/updateIncomeCash', { incomeCash }, options);
}

/** 更新分红 POST /api/divident */
export async function updateDividend(options?: RequestOptions) {
  return postRequest<API.DividentResult>('/api/divident', undefined, options);
}

