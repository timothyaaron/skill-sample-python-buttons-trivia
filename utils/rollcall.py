import utils

from config import settings
from utils import animations, directives  # , logger
from utils.display import Display


DEFAULT_BUTTON_ANIMATION_DIRECTIVES = {
    'button_down': directives.GadgetController.set_button_down_animation({
        'animations': animations.BasicAnimations.fade_out(1, "blue", 200)
    }),
    'button_up': directives.GadgetController.set_button_up_animation({
        'animations': animations.BasicAnimations.solid(1, "black", 100)
    })
}

"""
A template input handler configuration that will be
used as a starting point for the roll call input handler.

The final configuration is dynamically generated.
"""
ROLL_CALL_INPUT_HANDLER_CONFIG_TEMPLATE = {
    'timeout': 1000,
    'proxies': [],
    'recognizers': {
        'roll_call_all_buttons': {
            "type": "match",
            "fuzzy": True,
            "anchor": "end",
            "pattern": []
        }
    },
    'events': {
        'roll_call_complete': {
            'meets': ['roll_call_all_buttons'],
            'reports': 'matches',
            'shouldEndInputHandler': True,
            'maximumInvocations': 1
        },
        'roll_call_timeout': {
            'meets': ['timed out'],
            'reports': 'history',
            'shouldEndInputHandler': True
        }
    }
}


class Helper:
    @staticmethod
    def generate_input_handler_config(player_count, timeout):
        """
        Generates an input handler configuration, based on given number of players
        """
        print('ROLLCALL_HELPER: generate input handler config')

        player_count = int(player_count)

        """
        For roll call we will use a list of proxies because we won't
        know the Id of any of the buttons ahead of time.
        The proxies will be filld out dynamically in a loop below.
        """
        proxies = []

        """
        create a recognizer pattern that matches once when all
        the buttons have been pressed at least once.
        """
        all_buttons_pattern = []

        """
        create intermediate recognizers, one for first button,
        one for second button, etc. that will match when each
        of the buttons is pressed the first time (identifed by
        proxy)
        """
        intermediate_patterns = []

        """
        set up the proxies and recognizer patterns dynamically
        based on the number of players.
        """
        for i in range(player_count):
            name = f'btn{i + 1}'
            proxies.append(name)
            pattern_step = {
                "gadgetIds": [name],
                "action": "down",
            }
            all_buttons_pattern.append(pattern_step)
            if i < player_count - 1:
                # for all but the last player, add an intermediate recognizer
                intermediate_patterns.append([pattern_step])

            """
            create the input handler configuration object
            that defines the recognizers and events used for roll call
            the full definition will be filled in dynamically
            """
            config = dict(ROLL_CALL_INPUT_HANDLER_CONFIG_TEMPLATE)
            config['proxies'] = proxies
            config['timeout'] = timeout
            config['recognizers']['roll_call_all_buttons']['pattern'] = all_buttons_pattern

            """
            now fill in the dynamically generated recognizer and event
            definitions into the input handler configuration object
            """
            for i in range(len(intermediate_patterns)):
                name = f'roll_call_button_{i + 1}'
                config['recognizers'][name] = {
                    "type": "match",
                    "fuzzy": True,
                    "anchor": "end",
                    # each intermediate event has a corresponding recognizer
                    "pattern": intermediate_patterns[i],
                }
                config['events'][name] = {
                    'meets': [name],
                    'reports': 'matches',
                    # intermediate events don't stop the input handler!
                    'shouldEndInputHandler': False,
                    'maximumInvocations': 1,
                }

        return config

    @staticmethod
    def listen_for_roll_call(handler_input, config):
        print('ROLLCALL_HELPER: listen for roll call')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        session_attrs['input_handler_id'] = handler_input.request_envelope.request.request_id
        request_attrs['directives'].append(directives.GameEngine.start_input_handler(config))

        # Send Pre-Roll Call Animation to all connected buttons
        request_attrs['directives'].append(directives.GadgetController.set_idle_animation({
            'animations': settings.ANIMATIONS['pre_roll_call']
        }))
        # Send Button Down Event
        request_attrs['directives'].append(directives.GadgetController.set_button_down_animation({
            'animations': settings.ANIMATIONS['roll_call_checkin']
        }))

    @staticmethod
    def dispatch_game_engine_events(handler_input, events):
        print('ROLLCALL_HELPER: dispatch game engine events')
        # try to process events in order of importance
        # 1) first pass through to see if there are any non-timeout events
        for i in range(len(events)):
            if 'roll_call_complete' == events[i]['name']:
                Helper.handle_roll_call_complete(handler_input, events[i])
            elif events[i]['name'].startswith('roll_call_button'):
                Helper.handle_roll_call_button_check_in(handler_input, events[i])

        # 2) second pass through to see if there are any timeout events
        for i in range(len(events)):
            if 'roll_call_timeout' == events[i]['name']:
                Helper.handle_roll_call_timeout(handler_input, events[i])

    @staticmethod
    def handle_roll_call_complete(handler_input, event):
        print(f'ROLLCALL_HELPER: handle roll call complete: {event}')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        # Move to the button game state to begin the game
        session_attrs['STATE'] = settings.STATE['button_game']
        session_attrs['buttons'] = [
            {
                'button_id': event['gadgetId'],
                'count': i + 1,
            } for i, event in enumerate(event['inputEvents'])
        ]

        # clear animations on all other buttons that haven't been added to the game
        request_attrs['directives'].append(directives.GadgetController.set_idle_animation({
            'animations': animations.BasicAnimations.solid(1, "black", 100)
        }))
        # display roll call complete animation on all buttons that were added to the game
        request_attrs['directives'].append(directives.GadgetController.set_idle_animation({
            'targetGadgets': [b['button_id'] for b in session_attrs['buttons']],
            'animations': settings.ANIMATIONS['roll_call_complete']
        }))

        print(f"RollCall: resuming game play, from question: {session_attrs['current_question']}")

        current_prompts = None
        if settings.ROLLCALL['named_players']:
            # tell the next player to press their button.
            message = utils._('ROLL_CALL_HELLO_PLAYER', {
                player_number: len(session_attrs['buttons'])
            })
            current_prompts = message

        message = utils._('ROLL_CALL_COMPLETE', len(session_attrs['buttons']))
        mixed_output_speech = ''
        if current_prompts:
            mixed_output_speech = " ".join([
                current_prompts.output_speech,
                settings.AUDIO['roll_call_complete'],
                settings.pick_random(message['output_speech']),
            ])
        else:
            mixed_output_speech = " ".join([
                settings.AUDIO['roll_call_complete'],
                settings.pick_random(message['output_speech']),
            ])

        request_attrs.render(handler_input, message)
        request_attrs['output_speech'].append(mixed_output_speech)
        request_attrs['reprompt'].append(message['reprompt'])
        request_attrs['open_microphone'] = True

    # handles the case when the roll call process times out before all players are checked in
    @staticmethod
    def handle_roll_call_timeout(handler_input):
        print('ROLLCALL_HELPER: handling time out event during roll call')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        # Reset button animation for all buttons
        request_attrs['directives'].append(DEFAULT_BUTTON_ANIMATION_DIRECTIVES['button_down'])
        request_attrs['directives'].append(DEFAULT_BUTTON_ANIMATION_DIRECTIVES['button_up'])

        message = utils._('ROLL_CALL_TIME_OUT')
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['reprompt'].append(message['reprompt'])
        request_attrs['open_microphone'] = True

    @staticmethod
    def handle_roll_call_button_check_in(handler_input, event):
        print(f"ROLLCALL_HELPER: handle button press event: {event}")
        session_attrs = handler_input.attributes_manager.session_attributes

        button_id = event['inputEvents'][0]['gadgetId']
        buttons = session_attrs.buttons or []

        # Check to see if we already have this button registered and if so skip registration
        for i in range(len(buttons)):
            if buttons[i]['button_id'] == button_id:
                print(f"This button is already registered. GadgetId={button_id}")
                return

        button_number = len(buttons) + 1
        print(f"Found a new button. New button number: {button_number}")
        buttons.append({
            'count': button_number,
            'button_id': button_id,
        })
        session_attrs['buttons'] = buttons

        Helper.handlePlayerCheckedIn(handler_input, button_id, len(buttons))

    @staticmethod
    def handle_player_checked_in(handler_input, button_id, player_number):
        print(
            f'ROLLCALL_HELPER: handle new player checked in: '
            f'player_number = {player_number}, button_id = {button_id}'
        )
        request_attrs = handler_input.attributes_manager.request_attributes

        request_attrs['directives'].append(directives.GadgetController.set_idle_animation({
            'targetGadgets': [button_id],
            'animations': settings.ANIMATIONS['roll_call_button_added']
        }))
        request_attrs['directives'].append(directives.GadgetController.set_button_down_animation({
            'targetGadgets': [button_id],
            'animations': settings.ANIMATIONS['roll_call_checkin']
        }))

        if (settings.ROLLCALL['NAMED_PLAYERS']):
            # tell the next player to press their button.
            message = utils._('ROLL_CALL_HELLO_PLAYER', {
                player_number: player_number
            })
            current_prompts = message
            message = utils._('ROLL_CALL_NEXT_PLAYER_PROMPT', {
                player_number: player_number + 1
            })
            request_attrs['output_speech'].append(current_prompts['output_speech'])
            request_attrs['output_speech'].append("<break time='1s'/>")
            request_attrs['output_speech'].append(message['output_speech'])
            request_attrs['output_speech'].append(settings.AUDIO['waiting_for_roll_call'])

        request_attrs['open_microphone'] = False

    @staticmethod
    def start_roll_call(handler_input, message_key):
        print('ROLLCALL_HELPER: resume roll call')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes
        config = Helper.generate_input_handler_config(**{
            'player_count': session_attrs['player_count'],
            'timeout': 35000,  # allow 35 seconds for roll call to complete
        })
        Helper.listen_for_roll_call(handler_input, config)

        message = utils._(message_key)
        Display.render(handler_input, message)
        request_attrs['output_speech'].append(message['output_speech'])
        request_attrs['output_speech'].append(settings.AUDIO['waiting_for_roll_call'])
        request_attrs['open_microphone'] = True

        session_attrs['buttons'] = []


class RollCall:
    def start(handler_input, resuming_game, player_count):
        """Exported method that starts Roll Call."""
        print('ROLLCALL: start roll call')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        session_attrs['STATE'] = settings.STATES['rollcall']
        session_attrs['player_count'] = player_count
        session_attrs['buttons'] = []
        request_attrs['open_microphone'] = False

        message_key = 'ROLL_CALL_RESUME_GAME' if resuming_game else 'ROLL_CALL_CONTINUE'
        Helper.start_roll_call(handler_input, message_key)

    def cancel(handler_input):
        """Exported method that cancels an in-progress roll call."""
        print('ROLLCALL: canceling roll call')
        session_attrs = handler_input.attributes_manager.session_attributes

        del session_attrs['buttons']
        if session_attrs['input_handler_id']:
            # Stop the previous InputHandler if one was running
            request_attrs = handler_input.attributes_manager.request_attributes
            request_attrs['directives'].append(directives.GameEngine.stop_input_handler({
                'id': session_attrs['input_handler_id']
            }))

    @staticmethod
    def handle_events(handler_input, events):
        """
        Exported GameEngine event handler.
        Should be called to receive all GameEngine InputHandlerEvents
        """
        return Helper.dispatch_game_engine_events(handler_input, events)
