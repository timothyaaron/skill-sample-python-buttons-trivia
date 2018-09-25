import gettext

from config import messages, questions, settings


def _(key, data={}):
    if key == 'QUESTIONS':
        return questions.en_US

    else:
        output = dict(messages.en_US[key])
        for k in output:
            output[k] = output[k].format(**{**settings.GAME_OPTIONS, **data})

        return output
