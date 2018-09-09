from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name, is_request_type

from config import settings
from utils.directives import GadgetController


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
        session_attrs['STATE'] = settings.STATES['start_game']

        # Check to see if we have an active game
        player_count = session_attrs.get('player_count') or 0
        current_question = session_attrs.get('current_question') or 0
        valid_player_count = player_count and player_count <= settings.GAME_OPTIONS['max_players']
        game_in_progress = current_question < settings.GAME_OPTIONS['questions_per_game']

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
            GadgetController.set_idle_animation({
                'animations': settings.ANIMATIONS['intro'],
            })
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
            session_attrs['STATE'] == settings.STATES['start_game']
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
        valid_player_count = player_count and player_count <= settings.GAME_OPTIONS['max_players']

        if valid_player_count:
            if player_count == 1:
                session_attrs['STATE'] = settings.STATES['buttonless_game']
                #     let responseMessage = ctx.t('SINGLE_PLAYER_GAME_READY');
                messages = {
                    'output_speech': 'Single player game.',
                    'reprompt': 'No really. Single player game.',
                }
                #     ctx.render(handlerInput, responseMessage);
                request_attrs['output_speech'].append(settings.AUDIO['roll_call_complete'])
                request_attrs['output_speech'].append(messages['output_speech'])
                request_attrs['reprompt'].append(messages['reprompt'])

                request_attrs['open_microphone'] = True

            else:
                session_attrs['STATE'] = settings.STATES['rollcall']  # handled inside RollCall
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


class NoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("AMAZON.NoIntent")(handler_input) and
            session_attrs['STATE'] == settings.STATES['start_game']
        )

    def handle(self, handler_input):
        print('start_handlers.NoHandler ----------------------')
        request_attrs = handler_input.attributes_manager.request_attributes

        #   let responseMessage = ctx.t('DONT_RESUME_GAME');
        messages = {
            'output_speech': 'Ok, lets start a new game. How many players will be playing?',
            'reprompt': 'How many players?',
        }
        request_attrs['output_speech'].append(messages['output_speech'])
        request_attrs['reprompt'].append(messages['reprompt'])
        # ctx.render(handlerInput, responseMessage);
        request_attrs['open_microphone'] = True

        # Send intro animation
        request_attrs['directives'].append(
            GadgetController.set_idle_animation({
                'animations': settings.ANIMATIONS['intro'],
            })
        )

        # new game, delete all attributes
        handler_input.attributes_manager.session_attributes = {}

        return handler_input.response_builder.response


class YesHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attrs = handler_input.attributes_manager.session_attributes
        return (
            is_request_type("IntentRequest")(handler_input) and
            is_intent_name("AMAZON.YesIntent")(handler_input) and
            session_attrs['STATE'] == settings.STATES['start_game']
        )

    def handle(self, handler_input):
        print('start_handlers.YesHandler ----------------------')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        player_count = session_attrs['player_count']
        valid_player_count = player_count and player_count <= settings.GAME_OPTIONS['max_players']

        if valid_player_count:
            if player_count == 1:
                session_attrs['STATE'] = settings.STATES['buttonless_game']
                #     let responseMessage = ctx.t('SINGLE_PLAYER_GAME_READY');
                messages = {
                    'output_speech': 'Single player game.',
                    'reprompt': 'No really. Single player game.',
                }
                #     ctx.render(handlerInput, responseMessage);
                request_attrs['output_speech'].append(settings.AUDIO['roll_call_complete'])
                request_attrs['output_speech'].append(messages['output_speech'])
                request_attrs['reprompt'].append(messages['reprompt'])

                request_attrs['open_microphone'] = True

            else:
                buttons = session_attrs.get('buttons')
                resuming = buttons and len(buttons) == player_count
                # RollCall.start(handlerInput, resumingGame, sessionAttributes.playerCount);
        else:
            print('Resuming roll call, but starting from scratch.')

            # Send intro animation
            request_attrs['directives'].append(
                GadgetController.set_idle_animation({
                    'animations': settings.ANIMATIONS['intro'],
                })
            )

            #   let responseMessage = ctx.t('RESUME_GAME');
            messages = {
                'output_speech': (
                    'Ok, we will pick up where you left off. '
                    'How many players will be playing?'
                ),
                'reprompt': 'How many players?',
            }
            request_attrs['output_speech'].append(messages['output_speech'])
            request_attrs['reprompt'].append(messages['reprompt'])
            # ctx.render(handlerInput, responseMessage);
            request_attrs['open_microphone'] = True

        return handler_input.response_builder.response
