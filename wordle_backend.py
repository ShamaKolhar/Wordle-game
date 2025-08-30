import random

#python formatter [Black] has been used to present a clean code

def show_popup(game_state, content, mode="text"):
    #Display a popup message in the game
    game_state['popup_queue'].append((content, mode))
    return

def initialise_game(all_words_file="english_dict.txt", wordle_words_file=None, secret_word=None, max_guesses=6, word_length=5):
    #Initialize a new game of Wordle
    if max_guesses < 1:
        raise ValueError("Max guesses must be 1 or more")
    if word_length < 1:
        raise ValueError("Word length must be 1 letter or more")

    # Read word lists
    with open(all_words_file, 'r') as f:
        all_words = [word.strip().lower() for word in f if len(word.strip()) == word_length]
    
    if not all_words:
        raise ValueError("No valid words in all words file")

    # Handle wordle words list
    wordle_words = []
    if wordle_words_file:
        with open(wordle_words_file, 'r') as f:
            wordle_words = [word.strip().lower() for word in f if len(word.strip()) == word_length]
        if not wordle_words:
            raise ValueError("No valid words in wordle words file")
    else:
        wordle_words = all_words

    # Initialize game state
    if secret_word:
        if len(secret_word) != word_length:
            raise ValueError("The secret word is not of the correct length")
        secret_word = secret_word.lower()
    else:
        secret_word = random.choice(wordle_words)

    # Create empty grid and color grid
    grid = [['' for _ in range(word_length)] for _ in range(max_guesses)]
    colour_grid = [['w' for _ in range(word_length)] for _ in range(max_guesses)]

    # Initialize active letters for tracking used letters (optional feature)
    active_letters = {chr(i): True for i in range(ord('a'), ord('z')+1)}

    return {
        'secret_word': secret_word,
        'word_length': word_length,
        'max_guesses': max_guesses,
        'grid': grid,
        'colour_grid': colour_grid,
        'i': 0,
        'j': 0,
        'status': 'playing',
        'wordle_words_file': wordle_words_file,
        'all_words_file': all_words_file,
        'popup_queue': [],
        'active_letters': active_letters,
        'allowed_words': all_words  # Cache for performance
    }

def reset_game(game_state, secret_word=None):
    """Reset the game state for a new game."""
    word_length = game_state['word_length']
    max_guesses = game_state['max_guesses']
    
    if secret_word and len(secret_word) != word_length:
        raise ValueError("The secret word is not of the correct length")
    
    # Choose new secret word if none provided
    if not secret_word:
        with open(game_state['wordle_words_file'], 'r') as f:
            wordle_words = [word.strip().lower() for word in f if len(word.strip()) == word_length]
            if not wordle_words:
                raise ValueError("No valid words in wordle words file")
            # Force a different word than the current one
            current_word = game_state['secret_word']
            wordle_words = [w for w in wordle_words if w != current_word]
            if wordle_words:  # If there are other words available
                secret_word = random.choice(wordle_words)
            else:  # If somehow there's only one word in the list
                with open(game_state['all_words_file'], 'r') as f2:
                    all_words = [word.strip().lower() for word in f2 if len(word.strip()) == word_length]
                    all_words = [w for w in all_words if w != current_word]
                    secret_word = random.choice(all_words)

    # Reset grid and colors
    game_state['grid'] = [['' for _ in range(word_length)] for _ in range(max_guesses)]
    game_state['colour_grid'] = [['w' for _ in range(word_length)] for _ in range(max_guesses)]
    game_state['i'] = 0
    game_state['j'] = 0
    game_state['status'] = 'playing'
    game_state['secret_word'] = secret_word.lower()
    game_state['popup_queue'] = []
    game_state['active_letters'] = {chr(i): True for i in range(ord('a'), ord('z')+1)}

def validate_guess(game_state):
    """Validate if the current guess is valid."""
    current_guess = "".join(game_state['grid'][game_state['i']])
    
    # Check length
    if len(current_guess) != game_state['word_length']:
        return False
        
    # Check if word exists in allowed words
    return current_guess.lower() in game_state['allowed_words']

def process_guess(guess, secret_word):
    """Process a guess and return color codes."""
    if not guess or not secret_word:
        raise ValueError("Guess and secret word cannot be empty")
        
    if len(guess) != len(secret_word):
        raise ValueError("Guess and secret word must be the same length")

    result = ['-'] * len(guess)
    secret_letters = list(secret_word)
    guess_letters = list(guess)
    
    # Count occurrences of letters in secret word
    secret_letter_count = {}
    for letter in secret_word:
        secret_letter_count[letter] = secret_letter_count.get(letter, 0) + 1
    
    # First pass: mark green letters (exact matches)
    for i in range(len(guess)):
        if guess_letters[i] == secret_letters[i]:
            result[i] = 'g'
            # Decrease count for this letter
            secret_letter_count[guess_letters[i]] -= 1
            guess_letters[i] = None
    
    # Second pass: mark yellow letters
    for i in range(len(guess)):
        if guess_letters[i] is not None:  # Skip already marked letters
            if guess_letters[i] in secret_letter_count and secret_letter_count[guess_letters[i]] > 0:
                result[i] = 'y'
                secret_letter_count[guess_letters[i]] -= 1
            else:
                result[i] = '-'
    
    return result

def process_command(game_state, command):
    """Process a game command."""
    if game_state['status'] != 'playing' and command not in ['restart', '!', 'share', '@']:
        return False

    command = command.lower().strip()
    
    # Handle single letter input
    if len(command) == 1 and command.isalpha():
        if game_state['j'] >= game_state['word_length']:
            show_popup(game_state, "Can't add more letters\nUse clear or delete to edit your guess.")
            return True
        game_state['grid'][game_state['i']][game_state['j']] = command
        game_state['j'] += 1
        return True

    # Handle commands
    if command in ['delete', '-']:
        if game_state['j'] > 0:
            game_state['j'] -= 1
            game_state['grid'][game_state['i']][game_state['j']] = ''
        return True

    if command in ['clear', '_']:
        game_state['grid'][game_state['i']] = [''] * game_state['word_length']
        game_state['j'] = 0
        return True

    if command in ['enter', '+']:
        if game_state['j'] < game_state['word_length']:
            show_popup(game_state, "Invalid word\nUse clear or delete to edit your guess")
            return True
            
        if not validate_guess(game_state):
            show_popup(game_state, "Invalid word\nUse clear or delete to edit your guess")
            return True

        current_guess = "".join(game_state['grid'][game_state['i']])
        colors = process_guess(current_guess, game_state['secret_word'])
        game_state['colour_grid'][game_state['i']] = colors

        # Update active letters
        for idx, letter in enumerate(current_guess):
            if colors[idx] == '-':
                game_state['active_letters'][letter] = False

        # Check win/lose conditions
        if all(c == 'g' for c in colors):
            game_state['status'] = 'won'
            show_popup(game_state, "You won!")
            return False
            
        game_state['i'] += 1
        game_state['j'] = 0

        if game_state['i'] >= game_state['max_guesses']:
            game_state['status'] = 'lost'
            show_popup(game_state, f"You lose! The word was {game_state['secret_word']}")
            return False
        
        return True

    if command in ['restart', '!']:
        show_popup(game_state, f"You have chosen to restart! The word was {game_state['secret_word']}")
        show_popup(game_state, "Restarting game")
        reset_game(game_state)
        return True

    # Handle invalid commands
    show_popup(game_state, "Invalid command")
    return True