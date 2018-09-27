import random
import re

from similarity.jarowinkler import JaroWinkler

import utils
from config import settings
from utils.animations import BasicAnimations
from utils.directives import GadgetController, GameEngine
from utils.display import Display


jw = JaroWinkler()


class GameHelper:
    @staticmethod
    def find_best_match(user_answer, answers):
        return [
            {
                'target': answer,
                'rating': jw.similarity(answer, user_answer),
            } for answer in answers
        ]

    @staticmethod
    def normalize_answer(answer):
        normalized = str(answer).lower().strip()
        normalized = re.sub(r'(a|an|the) ', '', normalized)
        word_forms = {
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine',
            '0': 'zero',
        }

        return word_forms.get(normalized, normalized)

    @staticmethod
    def get_formatted_score_output(score_info):
        if score_info['score'] == 1:
            answer_count = "with a single correct answer,"
        elif score_info['score'] > 0:
            answer_count = f"with {score_info['score']} correct answers,"
        else:
            answer_count = "with no correct answers,"

        if len(score_info['players']) == 1:
            output = f"{answer_count} is player {score_info['players'][0]}"
        else:
            all_but_last = ', '.join(score_info['players'][0:-1])
            last_player = score_info['players'][-1]
            output = f"{answer_count} are players {all_but_last}, and {last_player}"

        return output

    @staticmethod
    def get_formatted_scores(handler_input, scores, player_count):
        print(f"Getting formatted scores for {player_count} with scores {scores}.")

        ordered_scores = GameHelper.get_ordered_score_groups(scores, player_count)
        print(f"Ordered_scores: {ordered_scores}")

        output_speech = ''
        message = {}

        if player_count == 1:
            if ordered_scores[0]['score'] == 0:
                message = utils._('SCORING_SINGLE_PLAYER_NO_ANSWERS')
            elif ordered_scores[0]['score'] == 1:
                message = utils._('SCORING_SINGLE_PLAYER_ONE_ANSWER')
            else:
                data = {'answer_count': ordered_scores[0]['score']}
                message = utils._('SCORING_SINGLE_PLAYER_MULTIPLE_ANSWERS', data)

            output_speech = f"{message['output_speech']}. "

        else:
            if len(ordered_scores) == 1:
                # handle the special case when all players are tied
                if ordered_scores[0]['score'] == 0:
                    message = utils._('SCORING_TIED_NO_ANSWERS')

                else:
                    if ordered_scores[0]['score'] == 1:
                        message = utils._('SCORING_TIED_ONE_ANSWER')
                    else:
                        data = {'answer_count': ordered_scores[0]['score']}
                        message = utils._('SCORING_TIED_MULTIPLE_ANSWERS', data)

                output_speech = f"{message['output_speech']} "

            else:
                for i, scores in enumerate(ordered_scores):
                    message = utils._('SCORING_MULTI_PLAYERS', {
                        'place': (1 + i),
                        'score_details': GameHelper.get_formatted_score_output(scores),
                    })
                    output_speech += f"{message['output_speech']}. "

        return output_speech

    @staticmethod
    def generate_round_summary_narration(handler_input, current_question, scores, player_count):
        print(f"generate_round_summary: question {current_question}, player_count {player_count}")
        questions_per_round = int(settings.GAME_OPTIONS['questions_per_round'])
        rounds_completed = (int(current_question) - 1) / questions_per_round

        intro_prompt = utils._('GAME_ROUND_SUMMARY_INTRO', {'round': int(rounds_completed)})
        outro_prompt = utils._('GAME_ROUND_SUMMARY_OUTRO')

        output_speech = (
            f"<break time='1s'/>{intro_prompt['output_speech']} "
            f"{GameHelper.get_formatted_scores(handler_input, scores, player_count)}"
            f"<break time='1s'/>{outro_prompt['output_speech']}<break time='1s'/>"
        )

        return output_speech

    @staticmethod
    def get_ordered_score_groups(scores, player_count):
        # add a 0 if player hasn't scored yet
        for i in range(player_count):
            scores[str(i + 1)] = scores.get(str(i + 1)) or 0

        # get all unique score values in highest-firest order
        score_values = list(set(scores.values()))
        score_values.sort()
        score_values.reverse()

        # add player_ids to scores
        ordered_groups = [
            {
                'score': v, 'players': [id for id, score in scores.items() if score == v]
            } for v in score_values
        ]

        return ordered_groups


class Game:
    """
    This file contains most of the game logic, while the actual intent & event request
    handler can be found in the gamePlayHandlers.js file.

    The game loop is as follows
     1) Determine where in the game we are beginning, somewhere in middle. Add
         any accumulated speech to the response.
     2) Find the next question from the ../config/questions.js library
     3) Ask the question and return a GameEngine.StartInputHandler directive
         https://developer.amazon.com/docs/gadget-skills/receive-echo-button-events.html
     4) When a button event comes in, send a voice prompt using the answerQuestion method
     5) Process the input, collect the right/wrong verbal response
     6) Pass this accumulated speech to the loop and start at the beginning of loop
    """

    @staticmethod
    def end_game(handler_input, reset_game):
        print('GAME: end game')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        # Clean the player state on the way out
        session_attrs.pop('repeat', None)
        session_attrs.pop('incorrect_answer_buttons', None)
        session_attrs.pop('correct', None)
        session_attrs.pop('answering_button', None)
        session_attrs.pop('answering_player', None)

        response_message = utils._('GAME_FINISHED' if reset_game else 'GAME_CANCELLED')
        # Display.render(handler_input, response_message)
        request_attrs['open_microphone'] = False
        handler_input.response_builder.set_should_end_session(True)

        if session_attrs['STATE'] == settings.STATES['button_game']:
            request_attrs['directives'].append(GadgetController.set_idle_animation({
                'target_gadgets': [b['button_id'] for b in session_attrs['buttons']],
                'animations': settings.ANIMATIONS['exit'],
            }))

        if reset_game:
            final_scores = GameHelper.get_formatted_scores(
                handler_input,
                session_attrs.get('scores'),
                session_attrs['player_count']
            )
            multi_player = session_attrs['STATE'] == settings.STATES['button_game']
            msg_key = 'GAME_FINISHED_INTRO' if multi_player else 'SINGLE_PLAYER_GAME_FINISHED_INTRO'
            game_finished_message = utils._(msg_key)

            if len(request_attrs['output_speech']) == 0:
                request_attrs['output_speech'].append("<break time='2s'/>")

            request_attrs['output_speech'].extend([
                game_finished_message['output_speech'],
                final_scores,
                "<break time='1s'/>",
                response_message['output_speech'],
            ])

            handler_input.attributes_manager.session_attributes = {}

        else:
            request_attrs['output_speech'].append(response_message['output_speech'])

    @staticmethod
    def stop_current_input_handler(handler_input):
        """Helper function to stop the active input handler if one exists"""
        print('GAME: stop current input handler')
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        if session_attrs['input_handler_id']:
            request_attrs['directives'].append(
                GameEngine.stop_input_handler(session_attrs['input_handler_id'])
            )

    @staticmethod
    def handle_game_input_event(handler_input):
        def _button_down(request_attrs, session_attrs, game_engine_events):
            print('GAME: handle_game_input_event: button_down_event')
            gadget_id = game_engine_events[0].input_events[0].gadget_id
            buttons = session_attrs['buttons']

            player = next((b for b in buttons if b['button_id'] == gadget_id), None)
            session_attrs['answering_button'] = player['button_id']
            session_attrs['answering_player'] = player['count']

            response_message = utils._('BUZZ_IN_DURING_PLAY', {'player_number': player['count']})
            request_attrs['output_speech'].append(settings.AUDIO['buzz_in'])
            request_attrs['output_speech'].append(response_message['output_speech'])
            request_attrs['reprompt'].append(response_message['reprompt'])
            request_attrs['open_microphone'] = True

            other_players = [b['button_id'] for b in buttons if b['button_id'] != gadget_id]
            Game.reset_animations(handler_input, other_players)

        def _time_out(request_attrs, session_attrs, game_engine_events):
            session_attrs.pop('correct', None)
            session_attrs.pop('answering_button', None)
            session_attrs.pop('answering_player', None)

            response_message = utils._('ANSWER_TIME_OUT_DURING_PLAY')
            request_attrs['output_speech'].append(response_message['output_speech'])
            request_attrs['reprompt'].append(response_message['reprompt'])
            request_attrs['open_microphone'] = True

        def _answer_interstitial(request_attrs, session_attrs, game_engine_events):
            questions = utils._('QUESTIONS')
            current_question = int(session_attrs.get('current_question', 1))
            shuffled_index = session_attrs['ordered_questions'][current_question - 1]
            trivia_question = next((q for q in questions if q['index'] == shuffled_index), None)

            data = {'question_number': current_question}
            response_message = utils._('ASK_QUESTION_DISPLAY', data)
            response_message['display_text'] = trivia_question['question']
            # Display.render(handler_input, response_message)

            Game.listen_for_answer(handler_input)

        data = {
            'request_attrs': handler_input.attributes_manager.request_attributes,
            'session_attrs': handler_input.attributes_manager.session_attributes,
            'game_engine_events': handler_input.request_envelope.request.events,
        }

        print(f"GAME: handle_game_input_event: {data['game_engine_events']}")

        {
            'button_down_event': _button_down,
            'time_out_event': _time_out,
            'answer_interstitial_event': _answer_interstitial,
        }.get(handler_input.request_envelope.request.events[0].name)(**data)

    @staticmethod
    def reset_animations(handler_input, buttons):
        print("GAME: reset_animations")
        request_attrs = handler_input.attributes_manager.request_attributes
        request_attrs['directives'].append(GadgetController.set_idle_animation({
            'target_gadgets': buttons,
            'animations': BasicAnimations.solid(1, "black", 100)
        }))
        request_attrs['directives'].append(GadgetController.set_button_down_animation({
            'target_gadgets': buttons,
            'animations': BasicAnimations.solid(1, "black", 100)
        }))

    @staticmethod
    def answer_question(handler_input):
        print("GAME: answer_question")
        request_env = handler_input.request_envelope
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        if not session_attrs['waiting_for_answer']:
            session_attrs.pop('correct', None)
            if int(session_attrs['current_question'] or 0) <= settings.GAME_OPTIONS['questions_per_game']:  # noqa
                Game.stop_current_input_handler(handler_input)
                message = utils._('ANSWER_BEFORE_QUESTION')
                request_attrs['output_speech'].append(message['output_speech'])
                request_attrs['reprompt'].append(message['reprompt'])
                request_attrs['open_microphone'] = True
                return
            else:
                Game.end_game(handler_input, True)
                return

        elif (
            session_attrs['STATE'] == settings.STATES['button_game'] and
            (not session_attrs.get('answering_button') or not session_attrs.get('answering_player'))
        ):
            session_attrs.pop('correct', None)
            message = utils._('ANSWER_WITHOUT_BUTTONS')
            request_attrs['output_speech'].append(message['output_speech'])
            request_attrs['open_microphone'] = False
            return

        # get the answer out of the request event
        answer = GameHelper.normalize_answer(request_env.request.intent.slots['answers'].value)
        if answer == '':
            message = utils._('MISUNDERSTOOD_ANSWER')
            request_attrs['output_speech'].append(message['output_speech'])
            request_attrs['reprompt'].append(message['reprompt'])
            request_attrs['open_microphone'] = True
            return

        session_attrs['waiting_for_answer'] = False

        # get the current question from the question bank so we can compare answers
        current_index = int(session_attrs.get('current_question') or 1)
        shuffled_index = session_attrs['ordered_questions'][current_index - 1]
        questions = utils._('QUESTIONS')
        current_question = next((q for q in questions if q['index'] == shuffled_index), None)

        answers = map(GameHelper.normalize_answer, current_question['answers'])
        correct_answer = GameHelper.normalize_answer(current_question['correct_answer'])
        matches = GameHelper.find_best_match(answer, answers)

        print(f"COMPARING '{answer}' to [{list(answers)}]: ({len(matches)} matches)")
        answered = False
        for match in matches:
            if (
                match['rating'] > settings.GAME_OPTIONS['answer_similarity'] and
                match['target'] == correct_answer
            ):
                session_attrs['current_question'] += 1

                if 'scores' not in session_attrs:
                    session_attrs['scores'] = {str(session_attrs['answering_player']): 1}
                elif str(session_attrs['answering_player']) in session_attrs['scores']:
                    session_attrs['scores'][str(session_attrs['answering_player'])] += 1
                else:
                    session_attrs['scores'][str(session_attrs['answering_player'])] = 1

                keys = {
                    True: 'SINGLE_PLAYER_CORRECT_ANSWER_DURING_PLAY',
                    False: 'CORRECT_ANSWER_DURING_PLAY',
                }
                is_buttonless = session_attrs['STATE'] == settings.STATES['buttonless_game']
                message = utils._(keys[is_buttonless], {
                    'player_number': session_attrs['answering_player']
                })
                request_attrs['output_speech'].append(settings.AUDIO['correct_answer'])
                request_attrs['output_speech'].append(message['output_speech'])
                session_attrs['correct'] = True
                session_attrs.pop('repeat', None)
                session_attrs.pop('incorrect_answer_buttons', None)

                print('Answer provided matched one of the expected answers!')
                answered = True
                break

        # if we looped through the answer without a match...
        if not answered:
            # in a buttonless game we will not repeat the question, just mark is wrong
            if session_attrs['STATE'] == settings.STATES['buttonless_game']:
                session_attrs['current_question'] += 1

                message = utils._('SINGLE_PLAYER_INCORRECT_ANSWER_DURING_PLAY', {
                    'player_number': session_attrs['answering_player']
                })
                request_attrs['output_speech'].append(settings.AUDIO['incorrect_answer'])
                request_attrs['output_speech'].append(message['output_speech'])
                session_attrs['correct'] = False

            # don't repeat if we've asked less the max answers per question
            # and there is at least one player available to answer
            # (each player only get's one shot at answering)
            elif not session_attrs.get('repeat') or (
                session_attrs['repeat'] < settings.GAME_OPTIONS['max_answers_per_question'] and
                session_attrs['repeat'] + 1 < session_attrs['player_count']
            ):
                print("Answer provided doesn't seem to match any answers -> repeat question")
                session_attrs['repeat'] = int(session_attrs.get('repeat') or 0) + 1

                # don't let the same player answer again
                answering_button = session_attrs['answering_button']
                if session_attrs.get('incorrect_answer_buttons'):
                    session_attrs['incorrect_answer_buttons'].append(answering_button)
                else:
                    session_attrs['incorrect_answer_buttons'] = [answering_button]

                message = utils._('INCORRECT_ANSWER_DURING_PLAY', {
                    'player_number': session_attrs['answering_player']
                })
                request_attrs['output_speech'].append(settings.AUDIO['incorrect_answer'])
                request_attrs['output_speech'].append(message['output_speech'])
                session_attrs['correct'] = False

            else:
                print("Answer provided doesn't seem to match any answers -> skip question")
                session_attrs['current_question'] += 1
                session_attrs.pop('repeat', None)
                session_attrs.pop('incorrect_answer_buttons', None)

                keys = {
                    True: 'INCORRECT_ANSWER_DURING_PLAY',
                    False: 'INCORRECT_ANSWER_TOO_MANY_TIMES',
                }
                is_end = session_attrs['current_question'] >= settings.GAME_OPTIONS['questions_per_game']  # noqa
                message = utils._(keys[is_end], {
                    'player_number': session_attrs['answering_player']
                })
                request_attrs['output_speech'].append(settings.AUDIO['incorrect_answer'])
                request_attrs['output_speech'].append(message['output_speech'])
                request_attrs['output_speech'].append("<break time='2s'/>")
                session_attrs['correct'] = False

        Game.ask_question(handler_input, True)

    @staticmethod
    def ask_question(handler_input, is_following):
        """
        gather the built responses, add them to the overall response
        retrieve and ask the next/same question
        """
        request_env = handler_input.request_envelope
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes
        questions = utils._('QUESTIONS')
        print(f"GAME: ask_question (currentQuestion = {session_attrs.get('current_question')})")

        if not is_following:
            # clean repeat state
            session_attrs.pop('repeat', None)
            session_attrs.pop('incorrect_answer_buttons', None)

        session_attrs['input_handler_id'] = request_env.request.request_id

        if 'current_question' in session_attrs:
            current_question = int(session_attrs['current_question'])
        else:
            session_attrs['current_question'] = current_question = 1

        if 'ordered_questions' not in session_attrs or (
            current_question == 1 and 'repeat' not in session_attrs
        ):
            if settings.GAME_OPTIONS['shuffle_questions']:
                print('GamePlay: producing ordered questions for new game (using shuffling)!')
                # if this is the first question, then shuffle the questions
                ordered_questions = [q['index'] for q in questions]
                random.shuffle(ordered_questions)
            else:
                print('GamePlay: producing ordered questions for new game (shuffling disabled)!')
                ordered_questions = [q['index'] for q in questions]

            ordered_questions = ordered_questions[:settings.GAME_OPTIONS['questions_per_game']]
            session_attrs['ordered_questions'] = ordered_questions

        if (
            current_question > len(session_attrs['ordered_questions']) or
            current_question > settings.GAME_OPTIONS['questions_per_game']
        ):
            return Game.end_game(handler_input, True)

        else:
            shuffle_question = session_attrs['ordered_questions'][current_question - 1]
            next_question = next((q for q in questions if q['index'] == shuffle_question), None)
            print(
                f"Ask question: {current_question} of "
                f"{settings.GAME_OPTIONS['questions_per_game']}, "
                f"next question {next_question}"
            )

        interstitial_delay = 6000 if is_following else 3000
        questions_per_round = int(settings.GAME_OPTIONS['questions_per_round'])

        if (
            current_question > 2 and 'repeat' not in session_attrs and
            (current_question - 1) % questions_per_round == 0
        ):
            interstitial_delay += 12000
            round_summary = GameHelper.generate_round_summary_narration(
                handler_input,
                session_attrs['current_question'],
                session_attrs.get('scores'),
                session_attrs['player_count'],
            )
            request_attrs['output_speech'].append(round_summary)

        if 'correct' in session_attrs:
            if session_attrs['correct']:
                keys = {
                    True: 'ANSWER_QUESTION_CORRECT_DISPLAY',
                    False: 'SINGLE_PLAYER_ANSWER_QUESTION_CORRECT_DISPLAY',
                }
                key = keys[session_attrs['STATE'] == settings.STATES['button_game']]
                image = settings.pick_random(settings.IMAGES['correct_answer'])
            else:
                keys = {
                    True: 'ANSWER_QUESTION_INCORRECT_DISPLAY',
                    False: 'SINGLE_PLAYER_ANSWER_QUESTION_INCORRECT_DISPLAY',
                }
                key = keys[session_attrs['STATE'] == settings.STATES['button_game']]
                image = settings.pick_random(settings.IMAGES['incorrect_answer'])

            message = utils._(key, {'player_number': session_attrs['answering_player']})
            message['image'] = image
            Display.render(handler_input, message)

        else:
            key = 'NEW_GAME' if current_question == 1 else 'RESUME'
            message = utils._(f'ASK_FIRST_QUESTION_{key}_DISPLAY')
            Display.render(handler_input, message)

        # use a shorter break for buttonless games
        break_time = 4 if session_attrs['STATE'] == settings.STATES['button_game'] else 1
        answers = f"<break time='{break_time}s'/> Is it "
        if next_question['answers']:
            if len(next_question['answers']) > 1:
                answers += ', '.join(next_question['answers'][:-1])
                answers += f", or, {next_question['answers'][-1]}"
            else:
                answers = next_question['answers'][0]

            answers += "?"

        request_attrs['output_speech'].append(next_question['question'])
        request_attrs['output_speech'].append(answers)

        if session_attrs['STATE'] == settings.STATES['button_game']:
            request_attrs['output_speech'].append(settings.AUDIO['waiting_for_buzz_in'])

            Game.animate_buttons_after_answer(handler_input)
            Game.send_answer_interstitial(handler_input, interstitial_delay)
            session_attrs.pop('answering_button', None)
            session_attrs.pop('answering_player', None)
        else:
            request_attrs['reprompt'].append(answers)

            session_attrs['waiting_for_answer'] = True
            session_attrs['answering_player'] = 1
            request_attrs['open_microphone'] = True

            message = utils._('ASK_QUESTION_DISPLAY', {'question_number': current_question})
            if session_attrs.get('correct') is True:
                message['image'] = settings.pick_random(settings.IMAGES['correct_answer'])
            elif session_attrs.get('correct') is False:
                message['image'] = settings.pick_random(settings.IMAGES['incorrect_answer'])
            Display.render(handler_input, message)

        session_attrs.pop('correct', None)

    @staticmethod
    def listen_for_answer(handler_input):
        print('GAME: listen_for_answer')
        request_env = handler_input.request_envelope
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        session_attrs['input_handler_id'] = request_env.request.request_id
        session_attrs['waiting_for_answer'] = True
        request_attrs['open_microphone'] = False

        # remove buttons that have answered this question incorrectly
        gadget_ids = [b['button_id'] for b in session_attrs['buttons']]
        incorrect_answer_buttons = session_attrs.get('incorrect_answer_buttons') or []
        gadget_ids = list(filter(lambda id: id not in incorrect_answer_buttons, gadget_ids))

        request_attrs['directives'].append(GameEngine.start_input_handler({
            'timeout': 25000,
            'recognizers': {
                'any_button_buzz_in': {
                    'type': 'match',
                    'fuzzy': False,
                    'anchor': 'start',
                    'gadgetIds': gadget_ids,
                    'pattern': [{'action': 'down'}],
                }
            },
            'events': {
                'button_down_event': {
                    'meets': ['any_button_buzz_in'],
                    'reports': 'matches',
                    'shouldEndInputHandler': True,
                    'maximumInvocations': 1
                },
                'time_out_event': {
                    'meets': ['timed out'],
                    'reports': 'history',
                    'shouldEndInputHandler': True
                }
            }
        }))
        request_attrs['directives'].append(GadgetController.set_button_down_animation({
            'target_gadgets': gadget_ids,
            'animations': settings.ANIMATIONS['buzz_in'],
        }))
        request_attrs['directives'].append(GadgetController.set_idle_animation({
            'target_gadgets': gadget_ids,
            'animations': settings.ANIMATIONS['listen_for_answer'],
        }))

    @staticmethod
    def send_answer_interstitial(handler_input, interstitial_delay):
        print('GAME: send_answer_interstitial')
        request_env = handler_input.request_envelope
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        session_attrs['input_handler_id'] = request_env.request.request_id
        request_attrs['directives'].append(GameEngine.start_input_handler({
            'timeout': interstitial_delay,
            'recognizers': {},
            'events': {
                'answer_interstitial_event': {
                    'meets': ['timed out'],
                    'reports': 'history',
                    'shouldEndInputHandler': True,
                }
            }
        }))
        request_attrs['open_microphone'] = False

    @staticmethod
    def animate_buttons_after_answer(handler_input):
        print('GAME: animate_buttons_after_answer')
        request_env = handler_input.request_envelope
        request_attrs = handler_input.attributes_manager.request_attributes
        session_attrs = handler_input.attributes_manager.session_attributes

        session_attrs['input_handler_id'] = request_env.request.request_id

        all_players = [b['button_id'] for b in session_attrs['buttons']]

        if 'correct' in session_attrs:
            other_players = [
                b['button_id'] for b in session_attrs['buttons'] if (
                    b['button_id'] != session_attrs['answering_button'] and
                    b['button_id'] not in session_attrs.get('incorrect_answer_buttons', [])
                )
            ]

            if session_attrs['answering_button']:
                key = 'correct_answer' if session_attrs['correct'] else 'incorrect_answer'
                request_attrs['directives'].append(GadgetController.set_idle_animation({
                    'target_gadgets': [session_attrs['answering_button']],
                    'animations': settings.ANIMATIONS[key],
                }))

            if other_players:
                key = 'correct_answer' if session_attrs['correct'] else 'incorrect_answer'
                request_attrs['directives'].append(GadgetController.set_idle_animation({
                    'target_gadgets': other_players,
                    'animations': settings.ANIMATIONS['buzz_in_other_players'],
                }))

        else:
            request_attrs['directives'].append(GadgetController.set_idle_animation({
                'target_gadgets': all_players,
                'animations': settings.ANIMATIONS['buzz_in_other_players'],
            }))

        request_attrs['directives'].append(GadgetController.set_button_down_animation({
            'target_gadgets': all_players,
            'animations': BasicAnimations.solid(1, 'black', 100),
        }))
        request_attrs['open_microphone'] = False
