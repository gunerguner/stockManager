/**
 * 状态码常量定义
 * 与后端 constants.py 保持一致
 */

/**
 * 业务响应状态码
 */
export const RESPONSE_STATUS = {
  /** 操作成功 */
  SUCCESS: 1,
  /** 操作失败 */
  ERROR: 0,
  /** 未登录/未授权 */
  UNAUTHORIZED: 302,
} as const;

/**
 * HTTP 状态码配置
 * 包含状态码和对应的错误信息
 */
const HTTP_STATUS_CONFIG = {
  OK: { code: 200, message: '服务器成功返回请求的数据。' },
  CREATED: { code: 201, message: '新建或修改数据成功。' },
  ACCEPTED: { code: 202, message: '一个请求已经进入后台排队（异步任务）。' },
  NO_CONTENT: { code: 204, message: '删除数据成功。' },
  BAD_REQUEST: { code: 400, message: '发出的请求有错误，服务器没有进行新建或修改数据的操作。' },
  UNAUTHORIZED: { code: 401, message: '用户没有权限（令牌、用户名、密码错误）。' },
  FORBIDDEN: { code: 403, message: '用户得到授权，但是访问是被禁止的。' },
  NOT_FOUND: { code: 404, message: '发出的请求针对的是不存在的记录，服务器没有进行操作。' },
  METHOD_NOT_ALLOWED: { code: 405, message: '请求方法不被允许。' },
  NOT_ACCEPTABLE: { code: 406, message: '请求的格式不可得。' },
  GONE: { code: 410, message: '请求的资源被永久删除，且不会再得到的。' },
  UNPROCESSABLE_ENTITY: { code: 422, message: '当创建一个对象时，发生一个验证错误。' },
  INTERNAL_SERVER_ERROR: { code: 500, message: '服务器发生错误，请检查服务器。' },
  BAD_GATEWAY: { code: 502, message: '网关错误。' },
  SERVICE_UNAVAILABLE: { code: 503, message: '服务不可用，服务器暂时过载或维护。' },
  GATEWAY_TIMEOUT: { code: 504, message: '网关超时。' },
} as const;

/**
 * HTTP 状态码对应的错误信息
 */
export const HTTP_CODE_MESSAGE: Record<number, string> = Object.fromEntries(
  Object.values(HTTP_STATUS_CONFIG).map(({ code, message }) => [code, message])
);

/**
 * 环境标签颜色配置
 */
export const ENV_TAG_COLORS = {
  dev: 'orange',
  test: 'green',
  pre: '#87d068',
} as const;

