from ask_sdk_model.interfaces.display import ImageInstance, TextContent

from config import settings


class Display:
    @staticmethod
    def render(handler_input, message):
        # # Check for display
        # if (!handlerInput.requestEnvelope.context.System.device.supportedInterfaces.Display) {
        #     logger.debug('No display to render.');
        #     return;
        # }

        if not message.get('display_text'):
            print('Render template without primary text!')

        text = message.get('display_text', '')
        if isinstance(text, list):
            text = settings.pick_random(text)

        subtext = message.get('display_subtext', '')
        if isinstance(subtext, list):
            subtext = settings.pick_random(subtext)

        background = (
            message.get('bg_image') or
            settings.pick_random(settings.IMAGES['background'])
        )

        template = {
            'type': 'BodyTemplate1',
            'backButton': 'HIDDEN',
            'backgroundImage': str(ImageInstance(background)),
            'title': message['display_title'],
            'textContent': str(TextContent(text, subtext)),
        }

        if message.get('image'):
            template['type']: 'BodyTemplate3'
            template['image']: str(ImageInstance(message['image']))

        # directive = template  # need to build the Display Directive

        # request_attrs['directives'].append(directive)
