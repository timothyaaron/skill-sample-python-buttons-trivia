"""
Use this file to configure the behavior of your trivia game.
"""
import random

from utils.animations import BasicAnimations, ComplexAnimations

"""
The skill ID to be matched against requests for confirmation.
It helps protect against spamming your skill.
Replace this with the value of your skill ID to enable this protection.
"""
APP_ID = None

"""
Game Settings
    MAX_PLAYERS - A number between 2 and 4
    QUESTIONS - The total number of questions you will ask per game. Must be
        less than or equal to the total number of questions in config/questions.js
    QUESTIONS_PER_ROUND - Number of questions you want to ask before giving a game summary.
        Should divide evenly into the total number of questions.
    ANSWER_SIMILARITY - A percentage value marking how similar an answer need to be to the
        correct answer to be considered correct. Used with the string-similarity package
        See github readme for setup instructions
    MAX_ANSWERS_PER_QUESTION - Maximum number of answers allowed for each question.
    SHUFFLE_QUESTIONS - if enabled, questions are presented in randomized order, otherwise
       each question is presented in the same answer as they are listed in the questions file.
"""
GAME_OPTIONS = {
    'max_players': 4,
    'questions_per_game': 6,
    'questions_per_round': 2,
    'answer_similarity': .60,
    'max_answers_per_question': 4,
    'shuffle_questions': True,
}

"""
Control how players register themselves for the game
    QUICK_START - Allows for all buttons up to GAME.MAX_PLAYERS to press their buttons during
        roll call before the skill will decide they are registered
    NAMED_PLAYERS - On each button press up to GAME.MAX_PLAYERS, acknowledge the button press
        and call the player out by name
"""
ROLLCALL_STATES = {
    'quick_start': False,
    'named_players': True,
}

"""
The name of the table in DynamoDB where you want to store session and game data.
You can leave this empty if you do not wish to use DynamoDB to automatically
store game data between sessions after each request.
"""
STORAGE = {
    'session_table': 'button_trivia'
}

"""
Change the behavior and colors of the buttons
    QUESTION_COLOR - The color the buttons will be when a question is asked.
        This is the signal to the users that they should buzz in
    BUZZ_IN_COLOR - The color to change the buttons to when someone buzzes in
    MISSED_BUZZ_IN - This is the color other buttons will turn when the first player
        buzzes in. In this case 'black' is off
    INCORRECT_COLOR - The color the button will blink when a player gets a question correct
    CORRECT_COLOR - The color a button will blink when the answering player gets the question
        correct.
"""
COLORS = {
    'question': 'purple',  # Color you want the buttons to be when expecting input
    'buzz_in': 'blue',  # Color you want the first button to chime in to be
    'missed_buzz_in': 'black',  # Color you want the other buttons who didn't chime in
    'incorrect': 'red',  # Incorrect answer color
    'correct': 'green',  # Correct color
    'exit': 'white',  # Exit color
}

"""
Links to sound effects used in the game
    ROLL_CALL_COMPLETE - Once all players have buzzed in, play this sound
    WAITING_FOR_BUZZ_IN_AUDIO - A ticking sound when the skill is waiting for a button press
    BUZZ_IN_AUDIO - The sound to play when a user 'buzzes in' and is ready to answer a question
    CORRECT_ANSWER_AUDIO - A sound effect to play when the users answer correctly
    INCORRECT_ANSWER_AUDIO - The sound effect to play when a user answers incorrectly
"""
base_url = 'https://s3.amazonaws.com/ask-soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow'
AUDIO = {
    'waiting_for_roll_call': f"<audio src='{base_url}_countdown_loop_32s_full_01.mp3'/>",
    'roll_call_complete': f"<audio src='{base_url}_intro_01.mp3'/>",
    'waiting_for_buzz_in': f"<audio src='{base_url}_waiting_loop_30s_01.mp3'/>",
    'buzz_in': f"<audio src='{base_url}_neutral_response_01.mp3'/>",
    'correct_answer': f"<audio src='{base_url}_positive_response_02.mp3'/>",
    'incorrect_answer': f"<audio src='{base_url}_negative_response_02.mp3'/>"
}

"""
A set of images to show on backgrounds and in display templates when the skill
is used with a device with a screen like the Echo Show or Echo Spot
https://developer.amazon.com/docs/custom-skills/display-interface-reference.html

The skill template chooses images randomly from each array to provide some
variety for the user.
"""
image_url = 'https://d2vbr0xakfjx9a.cloudfront.net'
IMAGES = {
    'background': [
        f'{image_url}/bg1.jpg',
        f'{image_url}/bg2.jpg'
    ],
    'correct_answer': [
        f'{image_url}/correct1.png',
        f'{image_url}/correct2.png',
        f'{image_url}/correct3.png',
        f'{image_url}/correct4.png'
    ],
    'incorrect_answer': [
        f'{image_url}/wrong1.png',
        f'{image_url}/wrong2.png',
        f'{image_url}/wrong3.png',
    ]
}

"""
Set up light animations that will be used throughout the game
    INTRO - Plays when a customer opens a Skill.
    PRE_ROLL_CALL - Buttons that are connected light up.
    ROLL_CALL_BUTTON_ADDED - Buttons that are connected light up.
    ROLL_CALL_COMPLETE - displays on all buttons in play
    ROLL_CALL_CHECKIN - buttons change state when added via roll call.
    BUZZ_IN - plays on answering players button
    BUZZ_IN_OTHER_PLAYERS - played for non-answering players buttons
    LISTEN_FOR_ANSWER - played to all buttons after a question is asked
    INCORRECT_ANSWER - Player gets something wrong.
    CORRECT_ANSWER - Player gets something right.
    EXIT - plays when the exiting the skill
"""
roll_call_complete_colors = ['red', 'orange', 'green', 'yellow', 'white']
ANIMATIONS = {
    'intro': ComplexAnimations.spectrum(10, ["red", "orange", "yellow"]),
    'pre_roll_call': BasicAnimations.fade_in(1, "white", 40000),
    'roll_call_button_added': BasicAnimations.solid(1, "green", 40000),
    'roll_call_complete': ComplexAnimations.spectrum(6, roll_call_complete_colors),
    'roll_call_checkin': BasicAnimations.solid(1, "green", 3000),
    'buzz_in': BasicAnimations.solid(1, COLORS['buzz_in'], 6000),
    'buzz_in_other_players': BasicAnimations.solid(1, 'black', 200),
    'listen_for_answer': BasicAnimations.solid(1, COLORS['question'], 26000),
    'incorrect_answer': ComplexAnimations.answer(COLORS['incorrect'], 'black', 1000),
    'correct_answer': ComplexAnimations.answer(COLORS['correct'], 'black', 1000),
    'exit': BasicAnimations.fade_out(1, COLORS['exit'], 1500),
}

"""
Define the different states that this skill can be in. For the Trivia skill,
we define ROLLCALL, GAME_LOOP, ROLLCALL_EXIT, and the initial state called
START_GAME_STATE (which maps to the initial state).

Start mode performs roll call and button registration.
https://developer.amazon.com/docs/gadget-skills/discover-echo-buttons.html
"""
STATES = {
    'start_game': '',
    'rollcall': '_ROLLCALL',
    'button_game': '_BUTTON_GAME',
    'buttonless_game': '_BUTTONLESS_GAME'
}


def pick_random(items):
    return random.choice(items) if isinstance(items, list) else items
