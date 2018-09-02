"""
Button Trivia Sample Port
"""
import os

import boto3
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractRequestInterceptor,
    AbstractResponseInterceptor,
)
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_dynamodb.adapter import DynamoDbAdapter


class ColorHelper:
    COLORS = {
        "white": "ffffff",
        "red": "ff0000",
        "orange": "ff3300",
        "green": "00ff00",
        "dark green": "004411",
        "blue": "0000ff",
        "light blue": "00a0b0",
        "purple": "4b0098",
        "yellow": "ffd400",
        "black": "000000"
    }

    @staticmethod
    def validate_color(color=''):
        if color[:2] == '0x':
            return color[2:]
        elif color[0] == '#':
            return color[1:]
        else:
            return ColorHelper.COLORS[color.lower()]


class ComplexAnimations:
    @staticmethod
    def spectrum_animation(cycles, colors):
        sequence = [
            {
                "blend": True,
                "duration": 400,
                "color": ColorHelper.validate_color(color),
            } for color in colors
        ]

        return [
            {
                "repeat": cycles,
                "targetLights": ["1"],
                "sequence": sequence,
            }
        ]


ENV = os.environ.get('ENV')
SETTINGS = {
    # 'skill_id': None,
    'storage': {'session_table': 'ButtonTrivia'},
    'state': {
        'START_GAME': '',
        'ROLLCALL': '_ROLLCALL',
        'BUTTON_GAME': '_BUTTON_GAME',
        'BUTTONLESS_GAME': '_BUTTONLESS_GAME',
    },
    'game': {
        'MAX_PLAYERS': 4,
        'QUESTIONS_PER_GAME': 6,
        'QUESTIONS_PER_ROUND': 2,
        'ANSWER_SIMILARITY': .60,
        'MAX_ANSWERS_PER_QUESTION': 4,
        'SHUFFLE_QUESTIONS': True,
    },
    'animations': {
        'INTRO': [10, ["red", "orange", "yellow"]],
    },
    'audio': {
        'ROLL_CALL_COMPLETE': "<audio src='https://s3.amazonaws.com/ask-soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_intro_01.mp3'/>",  # noqa
    }
}


adapter_config = {
    "table_name": SETTINGS['storage']['session_table'],
    "create_table": ENV == 'DEV',
}
if ENV == 'DEV':
    localhost = 'http://localhost:8000'
    adapter_config["dynamodb_resource"] = boto3.resource("dynamodb", endpoint_url=localhost)
else:
    adapter_config["dynamodb_resource"] = boto3.resource("dynamodb")


class GadgetController:
    @staticmethod
    def set_idle_animation(animations, target_gadgets=[], trigger_in=0):
        return {
            "type": "GadgetController.SetLight",
            "version": 1,
            "targetGadgets": target_gadgets,
            "parameters": {
                "animations": animations,
                "triggerEvent": "none",
                "triggerEventTimeMs": trigger_in,
            }
        }


class LaunchHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_request_type("LaunchRequest")(handler_input) or
            is_request_type("NewSession")(handler_input) or
            (
                is_request_type("IntentRequest")(handler_input) and
                is_intent_name("PlayGame")(handler_input)
            )
        )

    def handle(self, handler_input):
        print('LaunchHandler ----------------------')
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes
        persistent_attrs = attrs_manager.persistent_attributes
        session_attrs['STATE'] = SETTINGS['state']['START_GAME']

        # Check to see if we have an active game
        player_count = session_attrs.get('player_count') or 0
        current_question = session_attrs.get('current_question') or 0
        valid_player_count = player_count and player_count <= SETTINGS['game']['MAX_PLAYERS']
        game_in_progress = current_question < SETTINGS['game']['QUESTIONS_PER_GAME']

        # If there's an active game, resume; otherwise start a new game by asking how many players
        if valid_player_count and game_in_progress:
            message = {
                "output_speech": f"Restarting game with {player_count} players...",
                "reprompt": "Restarting."
            }
        else:
            message = {
                "output_speech": "Starting game...",
                "reprompt": "Starting."
            }

        # New game, so clear session attributes
        session_attrs = {}
        attrs_manager.session_attributes = session_attrs

        # Build response
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['reprompt'].append(message['reprompt'])
        # request_attrs.render(handler_input, message)
        request_attrs['open_microphone'] = True

        # Send intro animation
        request_attrs['directives'].append(
            GadgetController.set_idle_animation(SETTINGS['animations']['INTRO'])
        )

        return handler_input.response_builder.response


class StartNewGameHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("AMAZON.StartOverIntent")(handler_input)
        )

    def handle(self, handler_input):
        print('StartNewGameHandler ----------------------')
        del handler_input.attributes_manager.session_attributes['player_count']
        return LaunchHandler.handle(handler_input)


class PlayerCountHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            (
                is_intent_name("PlayerCount")(handler_input) or
                is_intent_name("PlayerCountOnly")(handler_input)
            ) and
            session_attrs['STATE'] == SETTINGS['state']['START_GAME']
        )

    def handle(self, handler_input):
        print('PlayerCountHandler ----------------------')
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes
        persistent_attrs = attrs_manager.persistent_attributes
        slots = handler_input.request_envelope.request.intent.slots

        player_count = int(slots["players"].value) if slots.get('players') else 0
        session_attrs['player_count'] = player_count
        valid_player_count = player_count and player_count <= SETTINGS['game']['MAX_PLAYERS']

        if valid_player_count:
            if player_count == 1:
                session_attrs['STATE'] = SETTINGS['state']['BUTTONLESS_GAME']
                #     let responseMessage = ctx.t('SINGLE_PLAYER_GAME_READY');
                messages = {
                    'output_speech': 'Single player game.',
                    'reprompt': 'No really. Single player game.',
                }
                #     ctx.render(handlerInput, responseMessage);
                request_attrs['output_speech'].append(SETTINGS['audio']['ROLL_CALL_COMPLETE'])
                request_attrs['output_speech'].append(messages['output_speech'])
                request_attrs['reprompt'].append(messages['reprompt'])

                request_attrs['open_microphone'] = True

            else:
                session_attrs['STATE'] = SETTINGS['state']['ROLLCALL']  # handled inside RollCall
                #     RollCall.start(handlerInput, false, sessionAttributes.playerCount);
        else:
            del session_attrs['STATE']  # bug? Can't save empty string to db

            #   let responseMessage = ctx.t('PLAYERCOUNT_INVALID');
            messages = {
                'output_speech': 'Please say a valid number.',
                'reprompt': 'Please say a valid number.',
            }
            request_attrs['output_speech'].append(messages['output_speech'])
            request_attrs['reprompt'].append(messages['reprompt'])
            request_attrs['open_microphone'] = True

        return handler_input.response_builder.response


class RequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        print('Request Intercepted')
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes
        persistent_attrs = attrs_manager.persistent_attributes

        # Ensure a state in case we're starting fresh
        if session_attrs.get('STATE') is None:
            session_attrs['STATE'] = SETTINGS['state']['START_GAME']
        elif session_attrs.get('STATE') == '_GAME_LOOP':
            session_attrs['STATE'] = SETTINGS['state']['BUTTON_GAME']

        # Apply the persistent attributes to the current session
        attrs_manager.session_attributes = {**persistent_attrs, **session_attrs}

        # Ensure we're starting at a clean state.
        request_attrs['directives'] = []
        request_attrs['output_speech'] = []
        request_attrs['reprompt'] = []

        # For ease of use we'll attach the utilities for rendering display
        # and handling localized tts to the request attributes
        # TODO


class ResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        print('Response Intercepted')
        response_builder = handler_input.response_builder
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes
        persistent_attrs = attrs_manager.persistent_attributes

        # Debug
        print(f'----- REQUEST ATTRIBUTES -----\n{request_attrs}')
        print(f'----- SESSION ATTRIBUTES -----\n{session_attrs}')
        print(f'----- PERSISTENT ATTRIBUTES -----\n{persistent_attrs}')

        # Build the speech response
        if len(request_attrs['output_speech']) > 0:
            output_speech = ' '.join(request_attrs['output_speech'])
            response_builder.speak(output_speech)

        if len(request_attrs['reprompt']) > 0:
            reprompt = ' '.join(request_attrs['reprompt'])
            response_builder.ask(reprompt)

        # Add the display response
        if request_attrs.get('render_template'):
            response_builder.add_render_template_directive(request_attrs['render_template'])

        response = response_builder.response

        # Apply the custom directives to the response
        if request_attrs.get('directives'):
            print(f"Processing {len(request_attrs['directives'])} custom directives")
            if not response.directives:
                response.directives = []
            response.directives += request_attrs['directives']

        if 'open_microphone' in request_attrs:
            if request_attrs.get('open_microphone'):
                response.should_end_session = False
            else:
                if request_attrs.get('end_session'):
                    response.should_end_session = True
                else:
                    response.should_end_session = False  # see NodeJS

        # Persist the current session attributes
        attrs_manager.persistent_attributes = session_attrs
        attrs_manager.save_persistent_attributes()

        print(f'----- NEW PERSISTENT ATTRIBUTES -----\n{persistent_attrs}')
        print(f'----- RESPONSE -----\n{response}')

        return response


sb = CustomSkillBuilder(persistence_adapter=DynamoDbAdapter(**adapter_config))
sb.skill_id = SETTINGS.get('skill_id')

sb.add_request_handler(LaunchHandler())
sb.add_request_handler(StartNewGameHandler())
sb.add_request_handler(PlayerCountHandler())
sb.add_global_request_interceptor(RequestInterceptor())
sb.add_global_response_interceptor(ResponseInterceptor())

handler = sb.lambda_handler()
