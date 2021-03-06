"""
Button Trivia Sample Port
"""
import os

import boto3
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

from config import settings
from handlers import game_play_handlers, global_handlers, start_handlers, roll_call_handlers

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

sb.add_request_handler(game_play_handlers.AnswerHandler())
sb.add_request_handler(game_play_handlers.DontKnowNextHandler())
sb.add_request_handler(game_play_handlers.GameEventHandler())
sb.add_request_handler(game_play_handlers.PlayGameHandler())
sb.add_request_handler(game_play_handlers.EndGameHandler())
sb.add_request_handler(game_play_handlers.YesHandler())
sb.add_request_handler(roll_call_handlers.YesHandler())
sb.add_request_handler(roll_call_handlers.NoHandler())
sb.add_request_handler(roll_call_handlers.GameEventHandler())
sb.add_request_handler(start_handlers.PlayerCountHandler())
sb.add_request_handler(start_handlers.YesHandler())
sb.add_request_handler(start_handlers.NoHandler())
sb.add_request_handler(start_handlers.LaunchPlayGameHandler())
sb.add_request_handler(start_handlers.StartNewGameHandler())
sb.add_request_handler(global_handlers.HelpHandler())
sb.add_request_handler(global_handlers.StopCancelHandler())
sb.add_request_handler(global_handlers.SessionEndedRequestHandler())
sb.add_request_handler(global_handlers.DefaultHandler())

sb.add_global_request_interceptor(global_handlers.RequestInterceptor())
sb.add_global_response_interceptor(global_handlers.ResponseInterceptor())

# sb.add_exception_handler(global_handlers.ErrorHandler())

handler = sb.lambda_handler()
