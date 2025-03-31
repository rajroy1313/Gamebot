
import random
import discord

def card_value(card):
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11
    return int(card)

def calculate_hand(hand):
    total = sum(card_value(card) for card in hand)
    aces = hand.count('A')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

class Blackjack:
    def __init__(self, bet):
        self.deck = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A'] * 4
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.game_over = False
        self.bet = bet

    def hit(self, hand):
        hand.append(self.deck.pop())

    def dealer_turn(self):
        while calculate_hand(self.dealer_hand) < 17:
            self.hit(self.dealer_hand)

    def game_result(self):
        player_total = calculate_hand(self.player_hand)
        dealer_total = calculate_hand(self.dealer_hand)
        if player_total > 21:
            return "You busted! Dealer wins.", -self.bet
        elif dealer_total > 21 or player_total > dealer_total:
            return "You win!", self.bet
        elif player_total < dealer_total:
            return "You lost!", -self.bet
        else:
            return "It's a tie!", 0
