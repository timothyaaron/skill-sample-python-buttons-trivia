import copy

from ask_sdk_model.interfaces.gadget_controller import (SetLightDirective,
                                                        SetLightParameters)
from ask_sdk_model.interfaces.game_engine import (StartInputHandlerDirective,
                                                  StopInputHandlerDirective)
from ask_sdk_model.services.gadget_controller import (AnimationStep,
                                                      LightAnimation,
                                                      TriggerEventType)
from ask_sdk_model.services.game_engine import (Event, EventReportingType,
                                                InputEventActionType, Pattern,
                                                PatternRecognizer,
                                                PatternRecognizerAnchorType)


class GameEngine:
    # Returns a StartInputHandler directive that can be added to an Alexa skill response
    @staticmethod
    def start_input_handler(params):
        events = [
            Event(**dict(
                e,
                reports=EventReportingType(e['reports'])
            )) for e in params['events'].values()
        ]
        recognizers = {}
        for name, recognizer in params['recognizers'].items():
            recognizer_notype = copy.deepcopy(recognizer)
            del recognizer_notype['type']
            anchor = PatternRecognizerAnchorType(params['recognizers'][name]['anchor'])
            recognizers[name] = PatternRecognizer(**dict(
                recognizer_notype,
                anchor=anchor,
                pattern=[
                    Pattern(
                        **dict(p, action=InputEventActionType(p['action']))
                    ) for p in recognizer['pattern']
                ]
            ))
        return StartInputHandlerDirective(
            events=events,
            proxies=params.get('proxies', []),
            recognizers=recognizers,
            timeout=params['timeout'],
        )

    # Returns a StopInputHandler directive that can be added to an Alexa skill response
    @staticmethod
    def stop_input_handler(id):
        return StopInputHandlerDirective(originating_request_=id)


class GadgetController:
    # returns a SetLight directive, with a 'buttonDown' trigger,
    # that can be added to an Alexa skill response
    @staticmethod
    def set_button_down_animation(params):
        animations = [
            LightAnimation(**dict(
                animation,
                sequence=[AnimationStep(**s) for s in animation['sequence']]
            )) for animation in params['animations']
        ]
        trigger_event = TriggerEventType('buttonDown')
        parameters = SetLightParameters(animations=animations, trigger_event=trigger_event,
                                        trigger_event_time_ms=params.get('trigger_time', 0))
        return SetLightDirective(version=1, target_gadget=params.get('target_gadgets', []),
                                 parameters=parameters)

    # returns a SetLight directive, with a 'buttonUp' trigger,
    # that can be added to an Alexa skill response
    @staticmethod
    def set_button_up_animation(params):
        animations = [
            LightAnimation(**dict(
                animation,
                sequence=[AnimationStep(**s) for s in animation['sequence']]
            )) for animation in params['animations']
        ]
        trigger_event = TriggerEventType('buttonUp')
        parameters = SetLightParameters(animations=animations, trigger_event=trigger_event,
                                        trigger_event_time_ms=params.get('trigger_time', 0))
        return SetLightDirective(version=1, target_gadget=params.get('target_gadgets', []),
                                 parameters=parameters)

    # returns a SetLight directive, with a 'none' trigger,
    # that can be added to an Alexa skill response
    @staticmethod
    def set_idle_animation(params):
        animations = [
            LightAnimation(**dict(
                animation,
                sequence=[AnimationStep(**s) for s in animation['sequence']]
            )) for animation in params['animations']
        ]
        trigger_event = TriggerEventType('none')
        parameters = SetLightParameters(animations=animations, trigger_event=trigger_event,
                                        trigger_event_time_ms=params.get('trigger_time', 0))
        return SetLightDirective(version=1, target_gadget=params.get('target_gadgets', []),
                                 parameters=parameters)
