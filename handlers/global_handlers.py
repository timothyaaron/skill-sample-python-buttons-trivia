from ask_sdk_core.dispatch_components import (
    AbstractExceptionHandler,
    AbstractRequestHandler,
    AbstractRequestInterceptor,
    AbstractResponseInterceptor,
)
from ask_sdk_core.utils import is_intent_name, is_request_type

import utils

from config import settings
from utils.display import Display


class RequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        print('Request Intercepted')
        attrs_manager = handler_input.attributes_manager
        request_attrs = attrs_manager.request_attributes
        session_attrs = attrs_manager.session_attributes
        persistent_attrs = attrs_manager.persistent_attributes

        # Ensure a state in case we're starting fresh
        if session_attrs.get('STATE') is None:
            session_attrs['STATE'] = settings.STATES['start_game']
        elif session_attrs.get('STATE') == '_GAME_LOOP':
            session_attrs['STATE'] = settings.STATES['button_game']
        # Apply the persistent attributes to the current session
        attrs_manager.session_attributes = {**persistent_attrs, **session_attrs}

        # Ensure we're starting at a clean state.
        request_attrs['directives'] = []
        request_attrs['output_speech'] = []
        request_attrs['reprompt'] = []


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

        # Adding display directives via Display.render, see next section
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


class DefaultHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return True

    def handle(self, handler_input):
        print('DefaultHandler ----------------------')
        request_attrs = handler_input.attributes_manager.request_attributes

        message = utils._('UNHANDLED_REQUEST')
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['reprompt'].append(message['reprompt'])
        request_attrs['open_microphone'] = True

        return handler_input.response_builder.response


class HelpHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        dont_know_ignore_states = [
            settings.STATES['button_game'],
            settings.STATES['buttonless_game'],
        ]
        return (
            is_request_type("IntentRequest")(handler_input) and
            (
                is_intent_name("AMAZON.HelpIntent")(handler_input) or
                (
                    is_intent_name("DontKnowIntent")(handler_input) and
                    session_attrs['STATE'] not in dont_know_ignore_states
                )
            )
        )

    def handle(self, handler_input):
        print('HelpHandler ----------------------')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        if session_attrs['STATE'] == settings.STATES['roll_call']:
            message_key = 'ROLL_CALL_HELP'
        elif session_attrs['STATE'] == settings.STATES['button_game']:
            message_key = 'GAME_PLAY_HELP'
            del session_attrs['answering_button']
            del session_attrs['answering_player']
            del session_attrs['correct']
        else:
            message_key = 'GENERAL_HELP'

        message = utils._(message_key)
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['reprompt'].append(message['reprompt'])
        # Display.render(handler_input, message)
        request_attrs['open_microphone'] = True

        return handler_input.response_builder.response


class StopCancelHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_request_type("IntentRequest")(handler_input) and
            (
                is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input)
            )
        )

    def handle(self, handler_input):
        print('StopCancelHandler ----------------------')
        request_attrs = handler_input.attributes_manager.request_attributes

        message = utils._('GOOD_BYE')
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['open_microphone'] = False
        handler_input.response_builder.set_should_end_session(True)

        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        print('SessionEndedRequestHandler ----------------------')
        session_attrs = handler_input.attributes_manager.session_attributes

        print(f'Reason: {handler_input.request_envelope.request.reason}')

        del session_attrs['STATE']
        handler_input.response_builder.set_should_end_session(True)

        return handler_input.response_builder.response


class ErrorHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(f"Handler -  {type(self).__name__}")
        print(f"ERROR - {exception}")

        text = "Uh oh. You've found an error. Please try again later."
        handler_input.response_builder.speak(text)

        return handler_input.response_builder.response
