from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """
    所有 Schema 的基类。
    - alias_generator=to_camel：字段名自动生成 camelCase 别名
      例：access_token → accessToken，tag_ids → tagIds
    - populate_by_name=True：同时允许用原始 snake_case 名称赋值
      （方便 Postman 调试 / 内部代码直接构造对象）
    FastAPI 在序列化响应时默认 by_alias=True，所以输出会自动是 camelCase。
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
