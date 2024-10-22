from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema, CoreSchema


class PyObjectId(ObjectId):

    @classmethod
    def _validate(cls, value, *args) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError(f'Invalid ObjectId: {value}')
        return ObjectId(value)

    @staticmethod
    def _serialize(value: 'PyObjectId') -> str:
        return str(value)

    @classmethod
    def __get_pydantic_core_schema__(cls, *args, **kwargs) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.any_schema(),
                when_used='json'
            )
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        return json_schema
