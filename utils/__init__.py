import gettext

from config import questions, settings


def _(key, data={}):
    if key == 'QUESTIONS':
        return questions.en_US

    else:
        i18n = gettext.translation('messages', localedir='locale', languages=['en_US'])

        types = ['output_speech', 'reprompt', 'display_title', 'display_text']
        messages = {}

        for type_ in types:
            expanded_key = f"{key}_{type_}"
            output = i18n.gettext(expanded_key)
            if output != expanded_key:
                messages[type_] = output.format(**{**settings.GAME_OPTIONS, **data})

        return messages
