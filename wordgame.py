
import random

class WordGame:
    def __init__(self):
        self.dictionary = [
            "python", "discord", "coding", "developer", "challenge", "programming",
            "algorithm", "function", "variable", "debugging"
        ]
        self.current_word = ""
        self.scrambled_word = ""
        
    def start_game(self):
        self.current_word = random.choice(self.dictionary)
        self.scrambled_word = ''.join(random.sample(self.current_word, len(self.current_word)))
        return self.scrambled_word

    def check_guess(self, guess):
        return guess.lower() == self.current_word

    def get_hint(self):
        if not self.current_word:
            return None
        return self.current_word[0] + ('_' * (len(self.current_word) - 1))

    def end_game(self):
        self.current_word = ""
        self.scrambled_word = ""
