from pydantic import BaseModel, validator, HttpUrl

from ..dependencies import validate_method_if_not_none, validate_method


class GetRules_Body(BaseModel):
    url: HttpUrl | None
    method: str | None
    
    @validator("method")
    def v_method(cls, v: str | None) -> str | None:
        return validate_method_if_not_none(v)

class CreateRules_Body(BaseModel):
    urls: list[HttpUrl]
    methods: list[str]
    requests: int
    refresh_rate: int
    
    @validator("methods")
    def v_methods_should_be_case_insensitive(cls, v: list[str]) -> list[str]:
        return [validate_method(method) for method in v]
    
    @validator("urls", "methods")
    def v_lists_cannot_be_empty(cls, v: list[str]) -> list[str]:
        if len(v) < 1:
            raise ValueError("cannot be empty")
        return v
    
    @validator("urls", "methods")
    def v_lists_should_be_unique(cls, v: list[str]) -> list[str]:
        if len(set(v)) != len(v):
            raise ValueError("all values should be unique")
        return v
    
    @validator("requests", "refresh_rate")
    def v_integers_should_be_more_than_zero(cls, v: int) -> int:
        if v < 1:
            raise ValueError("should be more than 0")
        return v

class DeleteRules_Body(BaseModel):
    url: HttpUrl
    method: str
    
    @validator("method")
    def v_method(cls, v: str | None) -> str | None:
        return validate_method(v)