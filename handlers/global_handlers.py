from ask_sdk_core.dispatch_components import (
    AbstractRequestInterceptor,
    AbstractResponseInterceptor,
)

from config import settings


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
