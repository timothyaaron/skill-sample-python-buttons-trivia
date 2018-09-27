from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, is_request_type

import utils

from config import settings
from utils.game import Game


class EndGameHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            (
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.NoIntent")(handler_input)
            ) and
            (
                session_attrs['STATE'] == settings.STATES['button_game'] or
                session_attrs['STATE'] == settings.STATES['buttonless_game']
            )
        )

    def handle(self, handler_input):
        print('EndGameHandler ----------------------')

        Game.end_game(handler_input, False)
        return handler_input.response_builder.response


class GameEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("GameEngine.InputHandlerEvent")(handler_input) and
            session_attrs['STATE'] == settings.STATES['button_game']
        )

    def handle(self, handler_input):
        print('GameEventHandler ----------------------')

        Game.handle_game_input_event(handler_input)
        return handler_input.response_builder.response


class PlayGameHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("PlayGame")(handler_input) and
            (
                session_attrs['STATE'] == settings.STATES['button_game'] or
                session_attrs['STATE'] == settings.STATES['buttonless_game']
            )
        )

    def handle(self, handler_input):
        print('PlayGameHandler ----------------------')
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes

        is_first_question = int(session_attrs.get('current_question', 0)) <= 1
        key = 'PLAY_GAME_FIRST_QUESTION' if is_first_question else 'PLAY_GAME_MID_GAME'
        message = utils._(key, {'current_question': session_attrs['current_question']})
        request_attrs['output_speech'].append(message['output_speech'])

        Game.ask_question(handler_input, False)
        return handler_input.response_builder.response


class YesHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("AMAZON.YesIntent")(handler_input) and
            (
                session_attrs['STATE'] == settings.STATES['button_game'] or
                session_attrs['STATE'] == settings.STATES['buttonless_game']
            )
        )

    def handle(self, handler_input):
        print('YesHandler ----------------------')

        Game.ask_question(handler_input, False)
        return handler_input.response_builder.response


class AnswerHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            (
                is_intent_name("AnswerQuestionIntent")(handler_input) or
                is_intent_name("AnswerOnlyIntent")(handler_input)
            ) and
            (
                session_attrs['STATE'] == settings.STATES['button_game'] or
                session_attrs['STATE'] == settings.STATES['buttonless_game']
            )
        )

    def handle(self, handler_input):
        print('AnswerHandler ----------------------')

        Game.answer_question(handler_input)
        return handler_input.response_builder.response


class DontKnowNextHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            (
                is_intent_name("DontKnowIntent")(handler_input) or
                is_intent_name("AMAZON.NextIntent")(handler_input)
            ) and
            (
                session_attrs['STATE'] == settings.STATES['button_game'] or
                session_attrs['STATE'] == settings.STATES['buttonless_game']
            )
        )

    def handle(self, handler_input):
        print('DontKnowNextHandler ----------------------')
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes

        session_attrs['current_question'] = int(session_attrs.get('current_question', 0)) + 1
        is_last_question = session_attrs['current_question'] > settings.GAME['questions_per_game']
        key = 'LAST' if is_last_question else 'SKIP'
        message = utils._(f"PLAY_GAME_{key}_QUESTION")
        request_attrs['output_speech'].append(f"{message['output_speech']}<break time='1s'/>")

        Game.ask_question(handler_input, False)
        return handler_input.response_builder.response
