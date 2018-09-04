from ask_skd_model.interfaces.display import ImageInstance, TextContent
from config import settings
# from utils import logger


class Display:
    def render(handler_input, display_title, display_text, bg_image, display_subtext="", image=""):
        request_attrs = handler_input.attributes_manager.request_attributes

        # # Check for display
        # if (!handlerInput.requestEnvelope.context.System.device.supportedInterfaces.Display) {
        #     logger.debug('No display to render.');
        #     return;
        # }

        if not display_text:
            print('Render template without primary text!')

        text = display_text or ''
        if isinstance(text, list):
            text = settings.pick_random(text)

        subtext = display_subtext or ''
        if isinstance(subtext, list):
            subtext = settings.pick_random(subtext)

        background = (
            bg_image or
            settings.pick_random(settings.IMAGES['background'])
        )

        template = {
            'type': 'BodyTemplate1',
            'backButton': 'HIDDEN',
            'backgroundImage': str(ImageInstance(background)),
            'title': display_title,
            'textContent': str(TextContent(text, subtext)),
        }

        if image:
            template['type']: 'BodyTemplate3'
            template['image']: str(ImageInstance(image))

        request_attrs.render_template(template)
