import gettext

from config import settings

i18n = gettext.translation('messages', localedir='locale', languages=['en_US'])


def _(key, data={}):
    types = ['output_speech', 'reprompt', 'display_title', 'display_text']
    messages = {}

    for type_ in types:
        expanded_key = f"{key}_{type_}"
        output = i18n.gettext(expanded_key)
        if output != expanded_key:
            messages[type_] = output.format(**{**settings.GAME_OPTIONS, **data})

    return messages
