// @ts-ignore
/* eslint-disable */
import { request } from 'umi';

const url = REACT_APP_ENV ? 'http://127.0.0.1:8000' : '';

/** 获取当前的用户 GET /api/currentUser */
export async function currentUser(options?: { [key: string]: any }) {
  return request<API.UserResult>(url + '/api/currentUser', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 登录接口 POST /api/login/outLogin */
export async function outLogin(options?: { [key: string]: any }) {
  return request<Record<string, any>>(url + '/api/logout', {
    method: 'POST',
    ...(options || {}),
  });
}

/** 登录接口 POST /api/login/account */
export async function login(body: API.LoginParams, options?: { [key: string]: any }) {
  return request<API.LoginResult>(url + '/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

export async function fetch(options?: { [key: string]: any }) {
  return request<API.StockResult>(url + '/api/', {
    method: 'GET',
    ...(options || {}),
  });
}

export async function updateOriginCash(cash: number, options?: { [key: string]: any }) {
  return request<API.BaseResult>(url + '/api/updateOriginCash', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: { cash: cash },
    ...(options || {}),
  });
}

export async function updateDivident(options?: { [key: string]: any }) {
  return request<API.DividentResult>(url + '/api/divident', {
    method: 'POST',
    ...(options || {}),
  });
}
