from upstash_redis import Redis
import os   

# 使用 Upstash Serverless Redis (HTTP 协议)
# 必须在 Azure 或本地的环境变量中配置以下两项：
# UPSTASH_REDIS_REST_URL
# UPSTASH_REDIS_REST_TOKEN
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL", "https://immune-wasp-75612.upstash.io")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "gQAAAAAAASdcAAIgcDEwNjk1YjhmOGI1MzI0ZDQ5OGQzYmNlMzk0OTBjZTYwZA")

redis_client = Redis(
    url=UPSTASH_REDIS_REST_URL, 
    token=UPSTASH_REDIS_REST_TOKEN
)

def get_redis():
    """获取 Upstash Redis 客户端"""
    return redis_client

    