import pytest
import os
from wordle_backend import initialise_game, process_command, process_guess, validate_guess

# Helper functions for test setup
def create_empty_file(filename):
    #Creates an empty file for testing
    with open(filename, 'w') as f:
        pass

def cleanup_test_files(filename):
    #Cleans up test files after testing
    if os.path.exists(filename):
        os.remove(filename)

# Test fixtures
@pytest.fixture(autouse=True)
def setup_teardown():
    #Setup and teardown for tests that require empty files
    create_empty_file("empty.txt")
    yield
    cleanup_test_files("empty.txt")

# Initialization tests
def test_initialise_game_default_values():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt")
    assert game_state['word_length'] == 5
    assert game_state['max_guesses'] == 6
    assert game_state['grid'] == [[''] * 5 for _ in range(6)]
    assert game_state['colour_grid'] == [['w'] * 5 for _ in range(6)]
    assert game_state['i'] == 0
    assert game_state['j'] == 0
    assert game_state['status'] == 'playing'
    assert game_state['wordle_words_file'] == "wordle_words.txt"
    assert game_state['all_words_file'] == "english_dict.txt"
    assert game_state['popup_queue'] == []

def test_initialise_game_invalid_max_guesses():
    with pytest.raises(ValueError, match="Max guesses must be 1 or more"):
        initialise_game(all_words_file="english_dict.txt", max_guesses=0)

def test_initialise_game_invalid_word_length():
    with pytest.raises(ValueError, match="Word length must be 1 letter or more"):
        initialise_game(all_words_file="english_dict.txt", word_length=0)

# Command processing tests
def test_process_command_enter_letter():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt")
    process_command(game_state, "a")
    assert game_state['grid'][0][0] == "a"
    assert game_state['j'] == 1

def test_process_command_delete_letter():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt")
    process_command(game_state, "a")
    process_command(game_state, "delete")
    assert game_state['grid'][0][0] == ""
    assert game_state['j'] == 0

def test_process_command_clear_guess():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt")
    for c in "stare":
        process_command(game_state, c)
    process_command(game_state, "clear")
    assert all(c == "" for c in game_state['grid'][0])
    assert game_state['j'] == 0

def test_process_command_enter_guess():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt", secret_word="stare")
    for c in "stare":
        process_command(game_state, c)
    process_command(game_state, "enter")
    assert game_state['colour_grid'][0] == ["g", "g", "g", "g", "g"]

# Validation tests
def test_validate_guess():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt")
    for c in "stare":  # Using a known valid word
        process_command(game_state, c)
    assert validate_guess(game_state) == True
    
    game_state['grid'][0] = list("xxxxx")  # Invalid word
    assert validate_guess(game_state) == False

# Game state tests
def test_win_game():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt", secret_word="stare")
    for c in "stare":
        process_command(game_state, c)
    process_command(game_state, "enter")
    assert game_state['status'] == "won"
    assert any("You won!" in msg[0] for msg in game_state['popup_queue'])

def test_lose_game():
    game_state = initialise_game(all_words_file="english_dict.txt", wordle_words_file="wordle_words.txt", secret_word="stare")
    wrong_word = "could"
    for _ in range(6):
        for c in wrong_word:
            process_command(game_state, c)
        process_command(game_state, "enter")
    assert game_state['status'] == "lost"
    assert any(f"You lose! The word was stare" in msg[0] for msg in game_state['popup_queue'])

# Exception tests
def test_no_valid_wordle_words():
    with pytest.raises(ValueError, match="No valid words in wordle words file"):
        initialise_game(all_words_file="english_dict.txt", wordle_words_file="empty.txt")

def test_no_valid_all_words():
    with pytest.raises(ValueError, match="No valid words in all words file"):
        initialise_game(all_words_file="empty.txt")

def test_secret_word_incorrect_length():
    with pytest.raises(ValueError, match="The secret word is not of the correct length"):
        initialise_game(all_words_file="english_dict.txt", secret_word="toolong")

def test_max_guesses_exception():
    with pytest.raises(ValueError, match="Max guesses must be 1 or more"):
        initialise_game(all_words_file="english_dict.txt", max_guesses=0)

def test_word_length_exception():
    with pytest.raises(ValueError, match="Word length must be 1 letter or more"):
        initialise_game(all_words_file="english_dict.txt", word_length=0)

# Process guess tests
def test_process_guess_all_correct():
    result = process_guess("stare", "stare")
    assert result == ["g", "g", "g", "g", "g"]

def test_process_guess_none_correct():
    result = process_guess("stare", "could")
    assert result == ["-", "-", "-", "-", "-"]

def test_process_guess_some_correct():
    result = process_guess("stare", "share")
    assert result == ["g", "-", "g", "g", "g"]

def test_process_guess_wrong_position():
    result = process_guess("stare", "erats")
    assert result == ["y", "y", "g", "y", "y"]

def test_process_guess_duplicate_letters():
    result = process_guess("hello", "below")  
    assert result == ["-", "g", "g", "-", "y"]