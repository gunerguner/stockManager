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
 * HTTP 状态码
 */
export const HTTP_STATUS = {
  /** 服务器成功返回请求的数据 */
  OK: 200,
  /** 新建或修改数据成功 */
  CREATED: 201,
  /** 一个请求已经进入后台排队（异步任务） */
  ACCEPTED: 202,
  /** 删除数据成功 */
  NO_CONTENT: 204,
  /** 发出的请求有错误，服务器没有进行新建或修改数据的操作 */
  BAD_REQUEST: 400,
  /** 用户没有权限（令牌、用户名、密码错误） */
  UNAUTHORIZED: 401,
  /** 用户得到授权，但是访问是被禁止的 */
  FORBIDDEN: 403,
  /** 发出的请求针对的是不存在的记录，服务器没有进行操作 */
  NOT_FOUND: 404,
  /** 请求方法不被允许 */
  METHOD_NOT_ALLOWED: 405,
  /** 请求的格式不可得 */
  NOT_ACCEPTABLE: 406,
  /** 请求的资源被永久删除，且不会再得到的 */
  GONE: 410,
  /** 当创建一个对象时，发生一个验证错误 */
  UNPROCESSABLE_ENTITY: 422,
  /** 服务器发生错误，请检查服务器 */
  INTERNAL_SERVER_ERROR: 500,
  /** 网关错误 */
  BAD_GATEWAY: 502,
  /** 服务不可用，服务器暂时过载或维护 */
  SERVICE_UNAVAILABLE: 503,
  /** 网关超时 */
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * 环境标签颜色配置
 */
export const ENV_TAG_COLORS = {
  dev: 'orange',
  test: 'green',
  pre: '#87d068',
} as const;

