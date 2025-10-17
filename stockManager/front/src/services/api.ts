// @ts-ignore
/* eslint-disable */
import { request } from 'umi';
import type { RequestOptionsInit } from 'umi-request';

// API基础地址配置
const API_BASE_URL = REACT_APP_ENV ? 'http://127.0.0.1:8000' : '';

// 通用JSON请求头
const JSON_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * 统一的GET请求封装
 */
const getRequest = <T>(endpoint: string, options?: RequestOptionsInit) => {
  return request<T>(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    ...options,
  });
};

/**
 * 统一的POST请求封装
 */
const postRequest = <T>(endpoint: string, data?: Record<string, unknown>, options?: RequestOptionsInit) => {
  return request<T>(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: JSON_HEADERS,
    data,
    ...options,
  });
};

/** 获取当前用户信息 GET /api/currentUser */
export async function getCurrentUser(options?: RequestOptionsInit) {
  return getRequest<API.UserResult>('/api/currentUser', options);
}

/** 用户登录 POST /api/login */
export async function login(params: API.LoginParams, options?: RequestOptionsInit) {
  return postRequest<API.LoginResult>('/api/login', params, options);
}

/** 用户登出 POST /api/logout */
export async function logout(options?: RequestOptionsInit) {
  return postRequest<Record<string, unknown>>('/api/logout', undefined, options);
}

/** 获取股票数据 GET /api/ */
export async function getStockList(options?: RequestOptionsInit) {
  return getRequest<API.StockResult>('/api/', options);
}

/** 更新原始资金 POST /api/updateOriginCash */
export async function updateOriginCash(cash: number, options?: RequestOptionsInit) {
  return postRequest<API.BaseResult>('/api/updateOriginCash', { cash }, options);
}

/** 更新收益资金 POST /api/updateIncomeCash */
export async function updateIncomeCash(incomeCash: number, options?: RequestOptionsInit) {
  return postRequest<API.BaseResult>('/api/updateIncomeCash', { incomeCash }, options);
}

/** 更新分红 POST /api/divident */
export async function updateDividend(options?: RequestOptionsInit) {
  return postRequest<API.DividentResult>('/api/divident', undefined, options);
}

// 保持向后兼容的别名（建议逐步迁移到新命名）
/** @deprecated 请使用 getCurrentUser */
export const currentUser = getCurrentUser;

/** @deprecated 请使用 logout */
export const outLogin = logout;

/** @deprecated 请使用 getStockList */
export const fetch = getStockList;

/** @deprecated 请使用 updateDividend */
export const updateDivident = updateDividend;
