import gettext

from config import messages, questions, settings


def _(key, data={}):
    if key == 'QUESTIONS':
        return questions.en_US

    else:
        output = dict(messages.en_US[key])
        for k in output:
            if isinstance(output[k], str):
                output[k] = output[k].format(**{**settings.GAME_OPTIONS, **data})
            elif isinstance(output[k], list):
                for i, o in enumerate(output[k]):
                    output[k][i] = o.format(**{**settings.GAME_OPTIONS, **data})

        return output
