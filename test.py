# import json
import main
import uuid
from datetime import datetime

from config import settings

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


def test_default():
    response = main.handler(new_request('NotAThingIntent'), context={})

    assert "Sorry, I didn't get that" in response['response']['outputSpeech']['ssml']
    assert "Please say it again" in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['response']['shouldEndSession'] is False


def test_launch():
    response = main.handler(new_request('LaunchRequest'), context={})

    assert 'Welcome to Even Better Button Trivia.' in response['response']['outputSpeech']['ssml']
    assert 'How many players' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {}
    assert response['response']['directives'][0]['type'] == 'GadgetController.SetLight'


def test_relaunch():
    request = new_request('LaunchRequest')
    request['session']['attributes'] = {
        'player_count': 2,
        'current_question': 2,
    }
    response = main.handler(request, context={})

    output = 'It looks like you have a 2 player'
    assert output in response['response']['outputSpeech']['ssml']
    assert 'Would you like to resume' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['response']['directives'][0]['type'] == 'GadgetController.SetLight'
    assert response['sessionAttributes'] == {}


def test_player_count_invalid():
    request = new_request('PlayerCount', {'players': 100})
    request['session']['attributes'] = {'STATE': settings.STATES['start_game']}
    response = main.handler(request, context={})

    assert 'between 1 and 4' in response['response']['outputSpeech']['ssml']
    assert 'between 1 and 4' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {
        'player_count': 100,
        'STATE': settings.STATES['start_game'],
    }


def test_player_count():
    request = new_request('PlayerCount', {'players': 1})
    request['session']['attributes'] = {'STATE': settings.STATES['start_game']}
    response = main.handler(request, context={})

    assert 'audio src=' in response['response']['outputSpeech']['ssml']
    assert 'Fantastic! Are you ready' in response['response']['outputSpeech']['ssml']
    assert 'Ready to start' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {
        'STATE': settings.STATES['buttonless_game'],
        'player_count': 1,
    }


def test_start_yes_invalid():
    request = new_request('AMAZON.YesIntent')
    request['session']['attributes'] = {
        'player_count': 99,
        'STATE': settings.STATES['start_game'],
    }
    response = main.handler(request, context={})

    assert 'How many players' in response['response']['outputSpeech']['ssml']
    assert 'How many players' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {
        'STATE': settings.STATES['start_game'],
        'player_count': 99,
    }


def test_start_yes_valid_one():
    request = new_request('AMAZON.YesIntent')
    request['session']['attributes'] = {
        'player_count': 1,
        'STATE': settings.STATES['start_game'],
    }
    response = main.handler(request, context={})

    assert 'audio src=' in response['response']['outputSpeech']['ssml']
    assert 'Fantastic! Are you ready' in response['response']['outputSpeech']['ssml']
    assert 'Ready to start' in response['response']['reprompt']['outputSpeech']['ssml']
    assert response['sessionAttributes'] == {
        'STATE': settings.STATES['buttonless_game'],
        'player_count': 1,
    }


def test_start_yes_valid_four():
    request = new_request('AMAZON.YesIntent')
    request['session']['attributes'] = {
        'player_count': 4,
        'STATE': settings.STATES['start_game'],
    }
    response = main.handler(request, context={})

    assert 'Ok. Players, press your buttons' in response['response']['outputSpeech']['ssml']
    assert response['response']['directives'][0]['type'] == 'GameEngine.StartInputHandler'
    assert response['response']['directives'][1]['type'] == 'GadgetController.SetLight'
    assert response['response']['directives'][2]['type'] == 'GadgetController.SetLight'
    assert 'input_handler_id' in response['sessionAttributes']
    assert response['sessionAttributes']['STATE'] == settings.STATES['rollcall']
    assert response['sessionAttributes']['player_count'] == 4
    assert response['sessionAttributes']['buttons'] == []


def test_end_session():
    response = main.handler(new_request('SessionEndedRequest'), context={})

    assert response['response'] == {'shouldEndSession': True}
