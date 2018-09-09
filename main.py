"""
Button Trivia Sample Port
"""
import os

import boto3
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

from config import settings
from handlers.start_handlers import (
    LaunchHandler,
    StartNewGameHandler,
    PlayerCountHandler,
)
from handlers.global_handlers import (
    RequestInterceptor,
    ResponseInterceptor,
)

ENV = os.environ.get('ENV')
adapter_config = {
    "table_name": settings.STORAGE['session_table'],
    "create_table": ENV == 'DEV',
}
if ENV == 'DEV':
    localhost = 'http://localhost:8000'
    adapter_config["dynamodb_resource"] = boto3.resource("dynamodb", endpoint_url=localhost)
else:
    adapter_config["dynamodb_resource"] = boto3.resource("dynamodb")


sb = CustomSkillBuilder(persistence_adapter=DynamoDbAdapter(**adapter_config))
sb.skill_id = settings.APP_ID

sb.add_request_handler(LaunchHandler())
sb.add_request_handler(StartNewGameHandler())
sb.add_request_handler(PlayerCountHandler())
sb.add_global_request_interceptor(RequestInterceptor())
sb.add_global_response_interceptor(ResponseInterceptor())

handler = sb.lambda_handler()
