"""缓存逻辑 key 与 TTL 常量"""

KEY_USER_OPERATIONS = "user:{user_id}:operations"
KEY_USER_CASH_INFO = "user:{user_id}:cash_info"
KEY_CALCULATED_TARGET = "user:{user_id}:calculated_target"
KEY_STOCK_META_ALL = "stock:meta:all"
KEY_STOCK_PRICE = "stock:price:{code}"
KEY_STOCK_PRICE_TIMESTAMP = "stock:price:timestamp"
KEY_STOCK_NAME_SYNC_MARK = "stock:name:sync:mark"

TTL_USER_DATA = 36000
TTL_CALCULATED_TARGET = 86400
TTL_STOCK_META = 86400
TTL_STOCK_PRICE = 86400
TTL_STOCK_NAME_SYNC = 86400
