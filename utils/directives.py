class GameEngine:
    # Returns a StartInputHandler directive that can be added to an Alexa skill response
    @staticmethod
    def start_input_handler(params):
        return {
            "type": "GameEngine.StartInputHandler",
            "timeout": params['timeout'],
            "recognizers": params['recognizers'],
            "events": params['events'],
            # "maximumHistoryLength": params.get('maximum_history', {}),
            "proxies": params.get('proxies', {}),
        }

    # Returns a StopInputHandler directive that can be added to an Alexa skill response
    @staticmethod
    def stop_input_handler(id):
        return {
            "type": "GameEngine.StopInputHandler",
            "originatingRequestId": id
        }


class GadgetController:
    # returns a SetLight directive, with a 'buttonDown' trigger, that can be added to an Alexa skill response
    @staticmethod
    def set_button_down_animation(params):
        return {
            "type": "GadgetController.SetLight",
            "version": 1,
            "targetGadgets": params.get('target_gadgets', []),
            "parameters": {
                "animations": params['animations'],
                "triggerEvent": "buttonDown",
                "triggerEventTimeMs": params.get('trigger_time', 0),
            }
        }

    # returns a SetLight directive, with a 'buttonUp' trigger, that can be added to an Alexa skill response
    @staticmethod
    def set_button_up_animation(params):
        return {
            "type": "GadgetController.SetLight",
            "targetGadgets": params.get('target_gadgets', []),
            "parameters": {
                "animations": params['animations'],
                "triggerEvent": "buttonUp",
                "triggerEventTimeMs": params.get('trigger_time', 0),
            }
        }

    # returns a SetLight directive, with a 'none' trigger, that can be added to an Alexa skill response
    @staticmethod
    def set_idle_animation(params):
        return {
            "type": "GadgetController.SetLight",
            "version": 1,
            "targetGadgets": params.get('target_gadgets', []),
            "parameters": {
                "animations": params['animations'],
                "triggerEvent": "none",
                "triggerEventTimeMs": params.get('trigger_time', 0),
            }
        }
