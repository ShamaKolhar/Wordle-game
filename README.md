# Wordle-game

Wordle (Python Backend)
A lightweight Python backend for the classic Wordle game. It manages game state, validates guesses, scores letters (green / yellow / gray), and supports simple command handling (type letters, backspace, enter, restart). Designed to be UI-agnostic so you can plug it into a CLI, web, or GUI front end.
Features
•	Initialize new games with custom word length & guess limit
•	Validates guesses against a dictionary
•	Scores guesses with familiar feedback (green / yellow / gray)
•	Queue-based popup messages for UX
•	Restart support and simple command processing
•	Unit tests with pytest
Repository Contents
wordle_backend.py   # Core game logic (init, validate, score, commands)
test_.py            # Unit tests (pytest)

Requirements
• Python 3.8+
• (Optional) pytest for tests

You’ll also need two word lists (one word per line):
 - english_dict.txt — allowed guess words (broad dictionary)
 - wordle_words.txt — (optional) candidate solutions; if omitted, a word is sampled from english_dict.txt
Quick Start
from wordle_backend import initialise_game, process_command

# Start a new game
game = initialise_game(all_words_file='english_dict.txt', wordle_words_file='wordle_words.txt', max_guesses=6, word_length=5)

# Type letters
for ch in 'stare':
    process_command(game, ch)

# Submit guess
process_command(game, 'enter')

# Read popup messages
while game['popup_queue']:
    msg, mode = game['popup_queue'].pop(0)
    print('[POPUP]', msg)
Command Reference
•	a–z : enter a letter into the current row
•	back or < : delete last letter
•	enter or return : submit current row as a guess
•	restart or ! : start a new game
Scoring Programmatically
from wordle_backend import process_guess

feedback = process_guess(secret='stare', attempt='share')  # returns ['g','-','y','-','-']
Validation
from wordle_backend import validate_guess

is_ok = validate_guess('stare', allowed_words_path='english_dict.txt', word_length=5)
Running Tests
pip install pytest
pytest -q
Customization
•	Word length: set word_length in initialise_game(...)
•	Max guesses: set max_guesses
•	Secret word: pass secret_word='abcde' for deterministic testing
•	Word lists: point to your own files
Notes
• Raises ValueError for invalid max_guesses or word_length
• Popups are queued in game_state['popup_queue'] for your UI to display
• Game status lives in game_state['status'] and turns are tracked internally
