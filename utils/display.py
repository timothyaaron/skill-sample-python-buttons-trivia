from ask_sdk_model.interfaces.display import (BackButtonBehavior,
                                              BodyTemplate1, BodyTemplate3,
                                              Image, ImageInstance,
                                              TextContent)
from config import settings


class Display:
    @staticmethod
    def render(handler_input, message):
        # Check for display
        if not handler_input.request_envelope.context.system.device.supported_interfaces.display:
            print('No display to render.')
            return

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

        data = {
            'back_button': BackButtonBehavior('HIDDEN'),
            'background_image': Image(sources=[ImageInstance(url=background)]),
            'title': message['display_title'],
            'text_content': str(TextContent(text, subtext)),
        }

        if message.get('image'):
            image = Image(sources=[ImageInstance(url=message['image'])])
            directive = BodyTemplate3(**data, image=image)
        else:
            directive = BodyTemplate1(**data)

        handler_input.attributes_manager.request_attributes['directives'].append(directive)
