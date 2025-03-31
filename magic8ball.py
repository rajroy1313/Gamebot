
import random

class Magic8Ball:
    def __init__(self):
        self.responses = [
            "Yes, definitely!",
            "No, absolutely not.",
            "Ask again later.",
            "It is certain.",
            "Very doubtful.",
            "Most likely.",
            "Better not tell you now.",
            "Signs point to yes.",
            "Cannot predict now.",
            "Don't count on it."
        ]

    def get_response(self, question):
        return random.choice(self.responses)
