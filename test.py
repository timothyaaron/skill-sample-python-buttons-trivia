# import json
import main
import uuid
from datetime import datetime

context = {}


def new_request(name, slots={}):
    is_intent = bool(name.endswith('Intent') or slots)
    app_id = f"amzn1.echo-sdk-ams.app.{uuid.uuid1()}"
    user_id = f"amzn1.ask.account.{uuid.uuid1()}"

    session = {
        "sessionId": f"amzn1.echo-api.session.{uuid.uuid1()}",
        "application": {
            "applicationId": app_id
        },
        "user": {
            "userId": user_id
        },
        "new": False,
    }
    request = {
        "requestId": f"amzn1.echo-api.request.{uuid.uuid1()}",
        "timestamp": f"{datetime.now().replace(second=0, microsecond=0).isoformat()}",
        "locale": "en-US",
        "type": "IntentRequest" if is_intent else name,
    }
    context = {
        "System": {
            "device": {
                "deviceId": "string",
                "supportedInterfaces": {
                    "AudioPlayer": {}
                  }
            },
            "application": {
                "applicationId": app_id
            },
            "user": {
                "userId": user_id,
                "accessToken": "Atza|AAAAAAAA...",
                "permissions": {
                    "consentToken": "ZZZZZZZ..."
                }
            },
            "apiEndpoint": "https://api.amazonalexa.com",
            "apiAccessToken": "AxThk..."
        },
        # "AudioPlayer": {
        #     "playerActivity": "PLAYING",
        #     "token": "audioplayer-token",
        #     "offsetInMilliseconds": 0
        # }
    }
    req_env = {
        "session": session,
        "request": request,
        "context": context,
    }

    if is_intent:
        req_env['request']['intent'] = {
            'name': name,
            'slots': {k: {'name': k, 'value': v} for k, v in slots.items()}
        }

    return req_env


def test_launch():
    response = main.handler(new_request('LaunchRequest'), context={})

    assert response['response']['outputSpeech']['ssml'] == '<speak>Starting game...</speak>'
    assert response['response']['reprompt']['outputSpeech']['ssml'] == '<speak>Starting.</speak>'
    assert response['sessionAttributes'] == {}
    assert response['response']['directives'][0]['type'] == 'GadgetController.SetLight'


def test_relaunch():
    request = new_request('LaunchRequest')
    request['session']['attributes'] = {
        'player_count': 2,
        'current_question': 2,
    }
    response = main.handler(request, context={})

    output = '<speak>Restarting game with 2 players...</speak>'
    assert response['response']['outputSpeech']['ssml'] == output
    assert response['response']['reprompt']['outputSpeech']['ssml'] == '<speak>Restarting.</speak>'
    assert response['response']['directives'][0]['type'] == 'GadgetController.SetLight'
    assert response['sessionAttributes'] == {}


def test_player_count_invalid():
    request = new_request('PlayerCount', {'players': 100})
    request['session']['attributes'] = {'STATE': ''}
    response = main.handler(request, context={})

    assert 'Please say a valid number.' in response['response']['outputSpeech']['ssml']
    assert 'Please say a valid number.' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {
        'player_count': 100,
    }


def test_player_count():
    request = new_request('PlayerCount', {'players': 1})
    request['session']['attributes'] = {'STATE': ''}
    response = main.handler(request, context={})

    assert 'audio src=' in response['response']['outputSpeech']['ssml']
    assert 'Single player game' in response['response']['outputSpeech']['ssml']
    assert 'No really. Single' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {
        'STATE': '_BUTTONLESS_GAME',
        'player_count': 1,
    }
