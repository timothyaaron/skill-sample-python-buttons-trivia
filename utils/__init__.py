import copy

from config import messages, settings


def _(key, data={}, locale='en_US'):
    output = copy.deepcopy(getattr(messages, locale)[key])

    if key != 'QUESTIONS':
        for k in output:
            if isinstance(output[k], str):
                output[k] = output[k].format(**{**settings.GAME_OPTIONS, **data})
            elif isinstance(output[k], list):
                for i, o in enumerate(output[k]):
                    output[k][i] = o.format(**{**settings.GAME_OPTIONS, **data})

    return output
