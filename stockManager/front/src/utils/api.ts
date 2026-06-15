import { RESPONSE_STATUS } from '@/utils/constants';

type ApiResponse = { status: number };

export const isApiSuccess = (res: ApiResponse): boolean =>
  res.status === RESPONSE_STATUS.SUCCESS;

export const isUnauthorized = (res: ApiResponse): boolean =>
  res.status === RESPONSE_STATUS.UNAUTHORIZED;

export const hasApiData = <T>(res: ApiResponse & { data?: T }): res is ApiResponse & { data: T } =>
  isApiSuccess(res) && res.data != null;
