en_US = {
    "GENERAL_HELP": {
        'output_speech': "To get started just ask me to play a game. What would you like to do? ",
        'reprompt': "Sorry, I didn't catch that, what would you like to do next?",
        'display_title': "{game_title} - Help",
        'display_text': "This is a trivia game for the Echo Buttons. To get started just ask me to play a game.",
    },
    "UNHANDLED_REQUEST": {
        'output_speech': "Sorry, I didn't get that. Please say again!",
        'reprompt': "Please say it again. You can ask for help if you're not sure what to do.",
    },
    "GOOD_BYE": {
        'output_speech': "Ok, see you next time!",
        'reprompt': "",
    },
    "START_GAME": {
        'output_speech': "Welcome to {game_title}. This game supports up to {max_players} players. How many players are there?",
        'reprompt': "How many players?",
        'display_title': "{game_title} - Welcome",
        'display_text': "Welcome to {game_title}. This game supports up to {max_players} players.",
    },
    "RESUME_GAME": {
        'output_speech': "Ok, we will pick up where you left off. How many players will be playing?",
        'reprompt': "How many players?",
        'display_title': "{game_title} - Welcome",
        'display_text': "Welcome back!",
    },
    "DONT_RESUME_GAME": {
        'output_speech': "Ok, lets start a new game. How many players will be playing?",
        'reprompt': "How many players?",
        'display_title': "{game_title} - Welcome",
        'display_text': "Ok. Let's start a new game!",
    },
    "ASK_TO_RESUME": {
        'output_speech': "It looks like you have a {player_count} player game in progress, would you like to resume?",
        'reprompt': "Would you like to resume the last game?",
        'display_title': "{game_title} - Welcome",
        'display_text': "You have a {player_count} player game in progress.",
    },
    "PLAYERCOUNT_INVALID": {
        'output_speech': "Please say a number between 1 and {max_players}",
        'reprompt': "Please say a number between 1 and {max_players}",
    },
    "SINGLE_PLAYER_GAME_READY": {
        'output_speech': "Fantastic! Are you ready to start the game?",
        'reprompt': "Ready to start the game?",
        'display_title': "{game_title} - Welcome",
        'display_text': "Are you ready to start the game?",
    },
    "ROLL_CALL_HELP": {
        'output_speech': "This is a trivia game for Echo Buttons. In order to play the game, each player must check in by pressing an Echo Button. Would you like to continue and check players in for the game?",
        'reprompt': "Sorry, I didn't catch that, what would you like to do next?",
        'display_title': "{game_title} - Help",
        'display_text': "In order to play the game, each player must check in by pressing an Echo Button. Would you like to continue?",
    },
    "ROLL_CALL_CONTINUE": {
        'output_speech': "Ok. Players, press your buttons now, so I'll know which buttons you will be using.",
        'display_title': "{game_title} - Welcome",
        'display_text': "To resume the game, each player, please press your button once!",
    },
    "ROLL_CALL_TIME_OUT": {
        'output_speech': "<say-as interpret-as='interjection'>Uh oh</say-as>, looks like times up and I haven't heard from all players. Did you want to continue?",
        'reprompt': "Should we continue?",
    },
    "ROLL_CALL_RESUME_GAME": {
        'output_speech': "To resume the game, each player, please press your button once!",
        'display_title': "{game_title} - Welcome",
        'display_text': "To resume the game, each player, please press your button once!",
    },
    "ROLL_CALL_COMPLETE": {
        'output_speech': [
            "Great! We can start the game. Are you ready?",
            "Awesome. All players registered. Are you ready to start the game?",
        ],
        'reprompt': "Ready to start the game?",
        'display_title': "{game_title} - Welcome",
        'display_text': "Are you ready to start the game?",
    },
    "ROLL_CALL_HELLO_PLAYER": {
        'output_speech': "Hello, player {player_number}. ",
    },
    "ROLL_CALL_NEXT_PLAYER_PROMPT": {
        'output_speech': "Ok, your turn Player {player_number}, press your button.",
    },
    "GAME_CANCELLED": {
        'output_speech': "Ok, see you next time! We'll save this game for later if you'd like to resume",
        'reprompt': "",
        'display_text': "See you next time!",
        'display_title': "Thanks for playing!",
    },
    "GAME_FINISHED_INTRO": {
        'output_speech': "The game is finished. Let's hear the final scores.",
    },
    "SINGLE_PLAYER_GAME_FINISHED_INTRO": {
        'output_speech': "The game is finished. Let's hear your final score.",
    },
    "GAME_FINISHED": {
        'output_speech': "Thanks for playing!",
        'reprompt': "",
        'display_text': "See you next time!",
        'display_title': "Thanks for playing!",
    },
    "PLAY_GAME_FIRST_QUESTION": {
        'output_speech': "Ok! Let's start the game!",
    },
    "PLAY_GAME_SKIP_QUESTION": {
        'output_speech': "Alright. Let's try another question.",
    },
    "PLAY_GAME_SKIP_LAST_QUESTION": {
        'output_speech': "Alright. That was the last question.",
    },
    "PLAY_GAME_MID_GAME": {
        'output_speech': "Ok! Let's keep going. We are on question {current_question}!",
    },
    "ANSWER_TIME_OUT_DURING_PLAY": {
        'output_speech': "I didn't hear any presses. Would you like to keep playing?",
        'reprompt': "Would you like to keep playing?",
    },
    "BUZZ_IN_DURING_PLAY": {
        'output_speech': "Ok, player {player_number}, what's the answer?",
        'reprompt': "Player {player_number}, are you there?",
    },
    "CORRECT_ANSWER_DURING_PLAY": {
        'output_speech': "Correct! Great job player {player_number}.",
    },
    "INCORRECT_ANSWER_DURING_PLAY": {
        'output_speech': "Sorry, wrong answer player {player_number}.",
    },
    "INCORRECT_ANSWER_TOO_MANY_TIMES": {
        'output_speech': "Sorry, wrong answer player {player_number}. Let's try another question.",
    },
    "SINGLE_PLAYER_CORRECT_ANSWER_DURING_PLAY": {
        'output_speech': "Correct! Great job.",
    },
    "SINGLE_PLAYER_INCORRECT_ANSWER_DURING_PLAY": {
        'output_speech': "Sorry, wrong answer.",
    },
    "MISUNDERSTOOD_ANSWER": {
        'output_speech': "Sorry, I didn't get that. Please say again!",
        'reprompt': "Please repeat the answer.",
    },
    "ANSWER_WITHOUT_BUTTONS": {
        'output_speech': "<say-as interpret-as='interjection'>Now, now</say-as>.<break time='1s'/>Press your button to answer the question!",
    },
    "ANSWER_BEFORE_QUESTION": {
        'output_speech': "I haven't asked the question yet! Wait for me to ask, then press your button if you know the answer! Are you ready?",
        'reprompt': "Are you ready to play?",
    },
    "ASK_QUESTION_DISPLAY": {
        'display_title': "{game_title} - Question {question_number}",
    },
    "ANSWER_QUESTION_CORRECT_DISPLAY": {
        'display_title': "{game_title} - Player {player_number}",
        'display_text': "Great job! That's right.",
    },
    "ANSWER_QUESTION_INCORRECT_DISPLAY": {
        'display_title': "{game_title} - Player {player_number}",
        'display_text': "Oops! That's not right.",
    },
    "SINGLE_PLAYER_ANSWER_QUESTION_CORRECT_DISPLAY": {
        'display_title': "{game_title}",
        'display_text': "Great job! That's right.",
    },
    "SINGLE_PLAYER_ANSWER_QUESTION_INCORRECT_DISPLAY": {
        'display_title': "{game_title}",
        'display_text': "Oops! That's not right.",
    },
    "ASK_FIRST_QUESTION_NEW_GAME_DISPLAY": {
        'display_title': "{game_title} - New Game",
        'display_text': "Get ready to start!",
    },
    "ASK_FIRST_QUESTION_RESUME_DISPLAY": {
        'display_title': "{game_title} - Resume Game",
        'display_text': "Get ready to start!",
    },
    "GAME_PLAY_HELP": {
        'output_speech': "This is a trivia game for Echo Buttons. During the game, I will ask one question at a time. If you know the answer, press your button for a chance to answer. You will earn a point for each question you answer correctly. Would you like to continue to play?",
        'reprompt': "Sorry, I didn't catch that, what would you like to do next?",
    },
    "GAME_PLAY_HELP": {
        'display_title': "{game_title} - Help",
        'display_text': "During the game, I will ask one question at a time. If you know the answer, press your button for a chance to answer. You will earn a point for each question you answer correctly.",
    },
    "GAME_ROUND_SUMMARY_INTRO": {
        'output_speech': "After the <say-as interpret-as='ordinal'>{round}</say-as> round.",
    },
    "GAME_ROUND_SUMMARY_OUTRO": {
        'output_speech': "Let's continue!",
    },
    "SCORING_TIED_NO_ANSWERS": {
        'output_speech': "It's a tie! With no correct answers. Can you do better?",
    },
    "SCORING_TIED_ONE_ANSWER": {
        'output_speech': "It's a tie! With a single correct answer. What a game!",
    },
    "SCORING_TIED_MULTIPLE_ANSWERS": {
        'output_speech': "It's a tie! With {answer_count} correct answers. What a game!",
    },
    "SCORING_SINGLE_PLAYER_NO_ANSWERS": {
        'output_speech': "You haven't answered any questions correctly",
    },
    "SCORING_SINGLE_PLAYER_ONE_ANSWER": {
        'output_speech': "You answered a single question correctly",
    },
    "SCORING_SINGLE_PLAYER_MULTIPLE_ANSWERS": {
        'output_speech': "You have {answer_count} correct answers",
    },
    "SCORING_MULTI_PLAYERS": {
        'output_speech': "In <say-as interpret-as='ordinal'>{place}</say-as> place, {score_details}",
    },
}