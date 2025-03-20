import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.game_over = False
    
    def print_board(self):
        return f"\n{self.board[0]} | {self.board[1]} | {self.board[2]}\n---------\n{self.board[3]} | {self.board[4]} | {self.board[5]}\n---------\n{self.board[6]} | {self.board[7]} | {self.board[8]}\n"
    
    def make_move(self, pos):
        if self.board[pos] == ' ' and not self.game_over:
            self.board[pos] = self.current_player
            if self.check_winner():
                self.game_over = True
                return f"Player {self.current_player} wins!"
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return None
        return "Invalid move. Try again."
    
    def check_winner(self):
        win_conditions = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != ' ':
                return True
        return False
    
    def reset(self):
        self.__init__()

game = TicTacToe()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def start(ctx):
    game.reset()
    await ctx.send("Tic-Tac-Toe game started! Use !move <position> (0-8) to play.\n" + game.print_board())

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
    await ctx.send("Game reset! Use !start to begin a new game.")

bot.run(MTM1MjI0MjMzMzU1MDI0Nzk3Ng.GBNaxa.IwNIbkpLcw1tO2HpgAq7ypIbcWf-PIeUk8p0Sk)
