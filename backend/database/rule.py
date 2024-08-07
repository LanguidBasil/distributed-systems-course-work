from dataclasses import dataclass
from redis import Redis

from ..utils import HTTPMethod


@dataclass(slots=True)
class Rule:
    url: str
    method: HTTPMethod

    refresh_rate: int
    requests: int


class RuleStorage:
    __connection: Redis

    def __init__(self, connection: Redis) -> None:
        self.__connection = connection

    def save(self, rule: Rule) -> None:
        self.__connection.hset(
            name=f"rules#{rule.url}#{rule.method.value}",
            mapping={
                "refresh_rate": rule.refresh_rate,
                "requests_max": rule.requests,
            },
        )

    def delete(self, url: str, method: HTTPMethod) -> bool:
        return bool(self.__connection.delete(f"rules#{url}#{method.value}"))

    def get(self, url: str = None, method: HTTPMethod = None) -> list[Rule]:
        if url is not None and method is not None:
            redis_rule = self.__connection.hgetall(f"rules#{url}#{method.value}")
            if not redis_rule:
                return []

            return [
                Rule(
                    url=url,
                    method=method,
                    refresh_rate=int(redis_rule["refresh_rate"]),
                    requests=int(redis_rule["requests_max"]),
                )
            ]

        pattern = f"rules#{url if url is not None else '*'}#{method.value if method is not None else '*'}"
        keys: list[str] = self.__connection.keys(pattern)

        rules = []
        for key in keys:
            redis_rule = self.__connection.hgetall(key)

            key = key.split("#")
            url, method = key[1], HTTPMethod(key[2])

            rules.append(
                Rule(
                    url=url,
                    method=method,
                    refresh_rate=int(redis_rule["refresh_rate"]),
                    requests=int(redis_rule["requests_max"]),
                )
            )

        return rules
