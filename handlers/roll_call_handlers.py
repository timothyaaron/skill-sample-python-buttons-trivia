from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, is_request_type

import utils

from config import settings
from utils.rollcall import RollCall


class GameEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("GameEngine.InputHandlerEvent")(handler_input) and
            session_attrs['STATE'] == settings.STATES['rollcall']
        )

    def handle(self, handler_input):
        print('GameEventHandler ----------------------')
        request_env = handler_input.request_envelope
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes

        if request_env.request.originatingRequestId != session_attrs['input_handler_id']:
            print(
                f"Global.GameEngineInputHandler: stale input event received -> "
                f"received event from {request_env.request.originatingRequestId} "
                f"(was expecting {session_attrs['input_handler_id']})"
            )
            request_attrs['open_microphone'] = False
            return handler_input.response_builder.response

        RollCall.handle_events(handler_input, request_env.request.events)
        return handler_input.response_builder.response


class NoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("AMAZON.NoIntent")(handler_input) and
            session_attrs['STATE'] == settings.STATES['rollcall']
        )

    def handle(self, handler_input):
        print('start_handlers.NoHandler ----------------------')
        request_attrs = handler_input.attributes_manager.request_attributes

        message = utils._('GOOD_BYE')
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['open_microphone'] = False
        handler_input.response_builder.set_should_end_session(True)

        return handler_input.response_builder.response


class YesHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("AMAZON.YesIntent")(handler_input) and
            session_attrs['STATE'] == settings.STATES['rollcall']
        )

    def handle(self, handler_input):
        print('RollCall.YesHandler ----------------------')
        session_attrs = handler_input.attributes_manager.session_attributes

        RollCall.start(handler_input, False, session_attrs['player_count'])

        return handler_input.response_builder.response
