"""缓存逻辑 key 与 TTL 常量"""

KEY_USER_OPERATIONS = "user:{user_id}:operations"
KEY_USER_CASH_INFO = "user:{user_id}:cash_info"
KEY_CALCULATED_TARGET = "user:{user_id}:calculated_target"
KEY_STOCK_META_ALL = "stock:meta:all"
KEY_STOCK_PRICE = "stock:price:{code}"
KEY_STOCK_PRICE_TIMESTAMP = "stock:price:timestamp:{market}"
KEY_STOCK_NAME_SYNC_MARK = "stock:name:sync:mark"
KEY_FX_HKD_CNY = "fx:hkd_cny"
KEY_USER_WATCHLIST = "user:{user_id}:watchlist"
KEY_VALUATION = "stock:valuation:{code}"
KEY_HIST_HIGH = "stock:hist_high:{code}"

TTL_DAY = 86400
TTL_USER_DATA = 36000
TTL_CALCULATED_TARGET = TTL_DAY
TTL_STOCK_META = TTL_DAY
TTL_STOCK_PRICE = TTL_DAY
TTL_STOCK_NAME_SYNC = TTL_DAY
TTL_FX = TTL_DAY
TTL_VALUATION = TTL_DAY
TTL_HIST_HIGH = TTL_DAY
