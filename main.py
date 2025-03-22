import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import time
import random
import sys
import os

app = Flask('')


@app.route('/')
def home():
    return "Yah bro you have made it!"


def run():
    app.run(host='0.0.0.0', port=3000, debug=False)


Thread(target=run).start()

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_error(event, *args, **kwargs):
    print(f'Error in {event}:', file=sys.stderr)
    import traceback
    traceback.print_exc()


# Player storage
player_money = {}
player_scores = {}  # For word puzzle game
DEFAULT_BALANCE = 1000  # Starting money

# Word list for the puzzle
dictionary = [
    "python", "discord", "coding", "developer", "challenge", "programming",
    "algorithm", "function", "variable", "debugging"
]
current_word = ""
scrambled_word = ""


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
#blackjack 

#8b start
# Possible Magic 8-Ball responses
responses = [
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

class Magic8BallBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()  # Sync slash commands on bot startup

@bot.tree.command(name="8ball", description="Ask the Magic 8-Ball a question!")
async def magic_8ball(interaction: discord.Interaction, question: str):
    answer = random.choice(responses)
    await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")


#8b end

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
            return "Busted !", 0
#tic tac toi

class TicTacToe:

    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.game_over = False

    def print_board(self):
        return f"\n{self.board[0]} | {self.board[1]} | {self.board[2]}\n-------\n{self.board[3]} | {self.board[4]} | {self.board[5]}\n-------\n{self.board[6]} | {self.board[7]} | {self.board[8]}\n"

    def make_move(self, pos):
        if self.board[pos] == ' ' and not self.game_over:
            self.board[pos] = self.current_player
            if self.check_winner():
                self.game_over = True
                return f"Player {self.current_player} wins!"
            elif ' ' not in self.board:  # Draw condition
                self.game_over = True
                return "It's a draw!"
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return None
        return "Invalid move. Try again."

    def check_winner(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                          (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[
                    a] != ' ':
                return True
        return False

    def reset(self):
        self.__init__()

    def end(self):
        self.game_over = True
        self.board = [' ' for _ in range(9)]


game = TicTacToe()
blackjack_game = None


@bot.command()
async def balance(ctx):
    user = str(ctx.author.id)
    balance = player_money.get(user, DEFAULT_BALANCE)
    await ctx.send(f"{ctx.author.mention}, your balance is: ${balance}")


@bot.command()
async def blackjack(ctx, bet: int):
    global blackjack_game
    user = str(ctx.author.id)
    player_money[user] = player_money.get(user, DEFAULT_BALANCE)

    if bet > player_money[user] or bet <= 0:
        await ctx.send(
            f"{ctx.author.mention}, you don't have enough money or invalid bet amount!"
        )
        return

    player_money[user] -= bet
    blackjack_game = Blackjack(bet)
    await ctx.send(
        f"Blackjack started!\nYour bet: ${bet}\nYour hand: {blackjack_game.player_hand} (Total: {calculate_hand(blackjack_game.player_hand)})\nDealer shows: {blackjack_game.dealer_hand[0]}"
    )


@bot.command()
async def hit(ctx):
    global blackjack_game
    if not blackjack_game or blackjack_game.game_over:
        await ctx.send(
            "No active game! Use $blackjack <bet> to start a new game.")
        return

    blackjack_game.hit(blackjack_game.player_hand)
    total = calculate_hand(blackjack_game.player_hand)
    if total > 21:
        blackjack_game.game_over = True
        await ctx.send(
            f"You drew a card. Your hand: {blackjack_game.player_hand} (Total: {total})\nYou busted! Dealer wins."
        )
    else:
        await ctx.send(
            f"You drew a card. Your hand: {blackjack_game.player_hand} (Total: {total})"
        )


@bot.command()
async def stand(ctx):
    global blackjack_game
    if not blackjack_game or blackjack_game.game_over:
        await ctx.send(
            "No active game! Use $blackjack <bet> to start a new game.")
        return

    blackjack_game.dealer_turn()
    blackjack_game.game_over = True
    result, money_change = blackjack_game.game_result()
    user = str(ctx.author.id)
    player_money[user] += money_change + blackjack_game.bet
    await ctx.send(
        f"Dealer's hand: {blackjack_game.dealer_hand} (Total: {calculate_hand(blackjack_game.dealer_hand)})\n{result}\nYour new balance: ${player_money[user]}"
    )


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command()
async def tic_tac_toi(ctx):
    game.reset()
    await ctx.send(
        "Tic-Tac-Toe game started! Use $move <position> (0-8) to play.\n" +
        game.print_board())


@bot.command()
async def move(ctx, position: int):
    if 0 <= position < 9:
        result = game.make_move(position)
        if result:
            await ctx.send(result + "\n" + game.print_board())
        else:
            await ctx.send(game.print_board())
    else:
        await ctx.send("Invalid position! Use a number between 0 and 8.")


@bot.command()
async def reset(ctx):
    game.reset()
    await ctx.send("Game reset! Use $start to begin a new game.")


@bot.command()
async def end(ctx):
    game.end()
    await ctx.send("Game ended. Use $start to begin a new game.")
    if game.start(True):  #Corrected syntax here.
        await ctx.send("Game not started. Use $start to start a new game.")


@bot.command(name='wordgame')
async def word_game(ctx):
    global current_word, scrambled_word
    current_word = random.choice(dictionary)
    scrambled_word = ''.join(random.sample(current_word, len(current_word)))
    await ctx.send(f"🔤 Unscramble this word: **{scrambled_word}**")


@bot.command()
async def guess(ctx, word: str):
    global current_word
    if not current_word:
        await ctx.send(
            "No word puzzle active! Use $wordgame to start a new puzzle.")
        return
    user = str(ctx.author.id)
    if word.lower() == current_word:
        player_scores[user] = player_scores.get(user, 0) + 1
        await ctx.send(
            f"✅ Correct, {ctx.author.mention}! The word was **{current_word}**. Your score: {player_scores[user]}"
        )
        current_word = ""
    else:
        await ctx.send(f"❌ Wrong guess, {ctx.author.mention}. Try again!")


@bot.command()
async def hint(ctx):
    global current_word
    if not current_word:
        await ctx.send(
            "No word puzzle active! Use $wordgame to start a new puzzle.")
        return
    hint_letter = current_word[0] + ('_' * (len(current_word) - 1))
    await ctx.send(f"💡 Hint: The word starts with **{hint_letter}**")


@bot.command()
async def wordboard(ctx):
    if not player_scores:
        await ctx.send(
            "No scores yet! Start playing to get on the leaderboard.")
        return
    leaderboard_msg = "🏆 **Word Game Leaderboard** 🏆\n"
    sorted_scores = sorted(player_scores.items(),
                           key=lambda x: x[1],
                           reverse=True)
    for user, score in sorted_scores[:5]:  # Show top 5
        leaderboard_msg += f"<@{user}>: {score} points\n"
    await ctx.send(leaderboard_msg)


@bot.command(name='commands')
async def show_commands(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.dark_red())

    # Tic-Tac-Toe Commands
    embed.add_field(name="🎮 Tic-Tac-Toe",
                    value="""
$tic_tac_toi - Start a new game
$move <0-8> - Make a move
$reset - Reset the game
$end - End the game
""",
                    inline=False)

    # Blackjack Commands
    embed.add_field(name="🎲 Blackjack",
                    value="""
$balance - Check balance
$blackjack <bet> - Start game
$hit - Draw card
$stand - Stand hand
""",
                    inline=False)

    # Word Game Commands
    embed.add_field(name="📝 Word Game",
                    value="""
$wordgame - Start puzzle
$guess <word> - Make guess
$hint - Get hint
$wordboard - Show scores
""", 
                    inline=False)

        #8b Commands
 embed.add_field(name=" 🎱 Magic 8-Bot",
                       value="""
$8ball <question> - Ask the Magic 8-Ball a question""",
        await ctx.send
                    
                    inline=False)

    await ctx.send(embed=embed)


# Create a simple slash command
@bot.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, world!")


# Get Token
token = os.getenv("BOT_TOKEN")
if not token:
    print("Error: BOT_TOKEN environment variable not set!")
    exit(1)

bot.run(token)
