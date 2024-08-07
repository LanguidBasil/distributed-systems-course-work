from dataclasses import dataclass
from redis import Redis

from ..utils import HTTPMethod


@dataclass(slots=True)
class BucketAnalytics:
    url: str
    method: HTTPMethod
    ip_address: str
    timestamp: float

    was_allowed: bool


class BucketAnalyticsStorage:
    __connection: Redis

    def __init__(self, connection: Redis) -> None:
        self.__connection = connection

    def save(self, bucket: BucketAnalytics) -> None:
        self.__connection.hset(
            f"bucketsanalytics#{bucket.url}#{bucket.method.value}#{bucket.ip_address}#{bucket.timestamp}",
            mapping={
                "was_allowed": int(bucket.was_allowed),
            },
        )

    def get(self, url: str = None, method: HTTPMethod = None, ip_address: str = None) -> list[BucketAnalytics]:
        pattern = (
            "bucketsanalytics"
            f"#{url if url is not None else '*'}"
            f"#{method.value if method is not None else '*'}"
            f"#{ip_address if ip_address is not None else '*'}"
            "#*"
        )
        keys: list[str] = self.__connection.keys(pattern)

        buckets = []
        for key in keys:
            redis_bucket = self.__connection.hgetall(key)

            keys = key.split("#")
            url, method, ip_address, timestamp = (
                keys[1],
                HTTPMethod(keys[2]),
                keys[3],
                float(keys[4]),
            )

            buckets.append(
                BucketAnalytics(
                    url=url,
                    method=method,
                    ip_address=ip_address,
                    timestamp=timestamp,
                    was_allowed=redis_bucket["was_allowed"] == "1",
                )
            )

        return buckets
