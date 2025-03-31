import discord
from discord.ext import commands

import asyncio

import logging

# Set up Discord logging
discord.utils.setup_logging(level=logging.INFO)
from flask import Flask
from threading import Thread
import os
import sys

# Import game modules
from resources.blackjack_game import Blackjack, calculate_hand
from resources.tictactoe_game import TicTacToe
from resources.wordgame import WordGame
from resources.magic8ball import Magic8Ball
from resources.giveaway import Giveaway
from resources.gemma_chat import GemmaModel
from resources.leveling import LevelSystem
from resources.ticket_system import TicketSystem

# Initialize systems
level_system = LevelSystem()
ticket_system = TicketSystem()
gemma_model = GemmaModel()
LEVEL_CHANNEL_ID = None
TICKET_CHANNEL_ID = None
AI_CHAT_CHANNEL_ID = None  # Replace with your AI chat channel ID

# Flask server setup
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=3000)

Thread(target=run).start()

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Game instances
tictactoe_game = TicTacToe()
wordgame = WordGame()
magic8ball = Magic8Ball()
blackjack_game = None
giveaway_system = Giveaway() # Initialize Giveaway system

# Player storage
player_money = {}
player_scores = {}
DEFAULT_BALANCE = 1000
ADMIN_IDS = ['1310654136290639894']

# Error handling
@bot.event
async def on_error(event, *args, **kwargs):
    print(f'Error in {event}:', file=sys.stderr)
    import traceback
    traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
    elif isinstance(error, commands.errors.CommandRateLimited):
        await ctx.send("We are being rate limited by Discord. Please wait a moment and try again.")
    else:
        print(f"Command error: {error}")

# Add cooldowns to frequently used commands
@commands.cooldown(1, 3, commands.BucketType.user)
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
        embed = discord.Embed(title="Error", description="Insufficient funds or invalid bet amount!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    player_money[user] -= bet
    blackjack_game = Blackjack(bet)

    embed = discord.Embed(title="Blackjack Game Started!", color=discord.Color.green())
    embed.add_field(name="Your Bet", value=f"${bet}", inline=False)
    embed.add_field(name="Your Hand", value=f"{blackjack_game.player_hand} (Total: {calculate_hand(blackjack_game.player_hand)})", inline=False)
    embed.add_field(name="Dealer Shows", value=blackjack_game.dealer_hand[0], inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def hit(ctx):
    global blackjack_game
    if not blackjack_game or blackjack_game.game_over:
        embed = discord.Embed(title="Error", description="No active game! Use $blackjack <bet> to start a new game.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    blackjack_game.hit(blackjack_game.player_hand)
    total = calculate_hand(blackjack_game.player_hand)

    if total > 21:
        blackjack_game.game_over = True
        embed = discord.Embed(title="Blackjack - Bust!", color=discord.Color.red())
        embed.add_field(name="Your Hand", value=f"{blackjack_game.player_hand} (Total: {total})", inline=False)
        embed.add_field(name="Result", value="You busted! Dealer wins.", inline=False)
    else:
        embed = discord.Embed(title="Blackjack - Hit", color=discord.Color.blue())
        embed.add_field(name="Your Hand", value=f"{blackjack_game.player_hand} (Total: {total})", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def stand(ctx):
    global blackjack_game
    if not blackjack_game or blackjack_game.game_over:
        embed = discord.Embed(title="Error", description="No active game! Use $blackjack <bet> to start a new game.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    blackjack_game.dealer_turn()
    blackjack_game.game_over = True
    result, money_change = blackjack_game.game_result()
    user = str(ctx.author.id)
    player_money[user] += money_change + blackjack_game.bet

    # Set color based on game result
    color = discord.Color.green() if money_change > 0 else discord.Color.red() if money_change < 0 else discord.Color.blue()

    embed = discord.Embed(title="Blackjack Result", color=color)
    embed.add_field(name="Dealer's Hand", value=f"{blackjack_game.dealer_hand} (Total: {calculate_hand(blackjack_game.dealer_hand)})", inline=False)
    embed.add_field(name="Result", value=result, inline=False)
    embed.add_field(name="New Balance", value=f"${player_money[user]}", inline=False)
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print("Syncing commands...")
    await bot.tree.sync()
    print("Commands synced!")
    await bot.change_presence(
        status=discord.Status.do_not_disturb,
        activity=discord.Game(name="Use /commands")
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    # Level system
    if str(message.channel.id) == LEVEL_CHANNEL_ID:
        level_up = level_system.add_xp(str(message.author.id))
        if level_up:
            await message.author.send(f"🎉 Congratulations! You've reached level {level_up}!")
            
    # AI Chat
    if str(message.channel.id) == AI_CHAT_CHANNEL_ID:
        response = gemma_model.get_response(str(message.author.id), message.content)
        await message.reply(response)

    if bot.user.mentioned_in(message):
        embed = discord.Embed(
            title="👋 Hi there!",
            description="Use `/commands` to see what I can do!",
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

@bot.command()
async def level(ctx):
    info = level_system.get_level_info(str(ctx.author.id))
    embed = discord.Embed(title="Your Level", color=discord.Color.blue())
    embed.add_field(name="Level", value=info["level"])
    embed.add_field(name="XP", value=info["xp"])
    embed.add_field(name="Next Level", value=f"{info['level'] * 100 - info['xp']} XP needed")
    await ctx.author.send(embed=embed)

@bot.command()
async def ticket(ctx, *, issue: str):
    if str(ctx.channel.id) != TICKET_CHANNEL_ID:
        await ctx.send("Please use the designated ticket channel!")
        return
        
    ticket_id = ticket_system.create_ticket(str(ctx.author.id), str(ctx.channel.id), issue)
    embed = discord.Embed(title="Ticket Created", color=discord.Color.green())
    embed.add_field(name="Ticket ID", value=ticket_id)
    embed.add_field(name="Issue", value=issue)
    
    # Notify support team
    support_ping = " ".join([f"<@&{role_id}>" for role_id in ticket_system.support_role_ids])
    await ctx.send(f"{support_ping} New ticket created: {ticket_id}")
    
    await ctx.author.send(embed=embed)
    await ctx.message.delete()

@bot.command()
async def closeticket(ctx, ticket_id: str):
    user_roles = [str(role.id) for role in ctx.author.roles]
    if not ticket_system.has_permission(user_roles, ticket_system.support_role_ids + ticket_system.admin_role_ids):
        await ctx.send("You don't have permission to close tickets!")
        return
        
    if ticket_system.close_ticket(ticket_id):
        await ctx.send(f"Ticket {ticket_id} has been closed.")

@bot.command()
async def setticketroles(ctx, role_type: str, *role_ids: str):
    user_roles = [str(role.id) for role in ctx.author.roles]
    if not ticket_system.has_permission(user_roles, ticket_system.admin_role_ids):
        await ctx.send("Only admins can set ticket roles!")
        return
        
    if role_type.lower() == "support":
        ticket_system.set_roles(list(role_ids), ticket_system.admin_role_ids)
        await ctx.send("Support roles updated!")
    elif role_type.lower() == "admin":
        ticket_system.set_roles(ticket_system.support_role_ids, list(role_ids))
        await ctx.send("Admin roles updated!")
    else:
        await ctx.send("Invalid role type! Use 'support' or 'admin'")

# Welcome channel ID
WELCOME_CHANNEL_ID = "YOUR_WELCOME_CHANNEL_ID"  # Replace with your channel ID

@bot.event
async def on_member_join(member):
    # Send welcome message in welcome channel
    welcome_channel = member.guild.get_channel(int(WELCOME_CHANNEL_ID))
    if welcome_channel:
        member_count = len([m for m in member.guild.members if not m.bot])
        welcome_msg = f"Hello {member.mention}. Welcome to {member.guild.name}.\n"
        welcome_msg += f"You are the {member_count}th member of {member.guild.name}.\n"
        welcome_msg += f"Type \"!help\" or call <@&1317507027357929503> & <@&1335283575104344124> if you need help."
        
        embed = discord.Embed(
            description=welcome_msg,
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await welcome_channel.send(embed=embed)
    
    # Send DM to new member
    try:
        dm_msg = f"Hello {member.name}. Welcome to {member.guild.name}.\n"
        dm_msg += "Checkout rules and pick up roles."
        await member.send(dm_msg)
    except discord.Forbidden:
        pass  # Unable to send DM

@bot.event
async def on_guild_join(guild):
    # Try to find a suitable channel to send the welcome message
    channel = None
    for ch in guild.text_channels:
        if ch.permissions_for(guild.me).send_messages:
            channel = ch
            break

    if channel:
        embed = discord.Embed(
            title="Thanks for adding me! 🎮",
            description="Here are my game commands:\n`/commands` - View all available commands\n`/blackjack` - Play Blackjack\n`/tictactoe` - Play Tic-Tac-Toe\n`/wordgame` - Play Word Scramble",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)


@bot.command()
async def tictactoi(ctx):
    tictactoe_game.reset()
    embed = discord.Embed(title="Tic-Tac-Toe Game", color=discord.Color.blue())
    embed.add_field(name="Game Started!", value="Use $move <position> (0-8) to play.", inline=False)
    embed.add_field(name="Current Board", value=f"```{tictactoe_game.print_board()}```", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def move(ctx, position: int):
    if 0 <= position < 9:
        result = tictactoe_game.make_move(position)
        if result:
            await ctx.send(result + "\n" + tictactoe_game.print_board())
        else:
            await ctx.send(tictactoe_game.print_board())
    else:
        await ctx.send("Invalid position! Use a number between 0 and 8.")


@bot.command()
async def reset(ctx):
    tictactoe_game.reset()
    await ctx.send("Game reset! Use $start to begin a new game.")


@bot.command()
async def end(ctx):
    tictactoe_game.end()
    await ctx.send("Game ended. Use $start to begin a new game.")


@bot.command(name='wordgame')
async def word_game(ctx):
    await wordgame.start(ctx)


@bot.command()
async def guess(ctx, word: str):
    await wordgame.guess(ctx, word)


@bot.command()
async def hint(ctx):
    await wordgame.hint(ctx)


@bot.command()
async def wordboard(ctx):
    await wordgame.show_leaderboard(ctx)


@bot.command(name='commands')
async def show_commands(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.dark_red())  
    embed.add_field(name="use prefix $", value=""" """, inline=False)

    # Admin Commands
    embed.add_field(name="👑 Admin Only",
                    value="""
addmoney <user> <amount> - Add money to user's balance
endgiveaway <id> - End an active giveaway
reroll <id> - Reroll giveaway winner
""",
                    inline=False)

    # Magic 8 Ball Commands
    embed.add_field(name="🎱 Magic 8 Ball",
                    value="""
8b <question> - Ask the Magic 8 Ball a question
""",
                    inline=False)

    # Tic-Tac-Toe Commands
    embed.add_field(name="🎮 Tic-Tac-Toe",
                    value="""
tictactoi - Start a new game
move <0-8> - Make a move
reset - Reset the game
end - End the game
""",
                    inline=False)

    # Blackjack Commands
    embed.add_field(name="🎲 Blackjack",
                    value="""
balance - Check balance
blackjack <bet> - Start game
hit - Draw card
stand - Stand hand
""",
                    inline=False)

    # Word Game Commands
    embed.add_field(name="📝 Word Game",
                    value="""
wordgame - Start puzzle
guess <word> - Make guess
hint - Get hint
wordboard - Show scores
""", 
                    inline=False)


    await ctx.send(embed=embed)


@bot.tree.command(name="balance", description="Check your balance")
async def slash_balance(interaction: discord.Interaction):
    user = str(interaction.user.id)
    balance = player_money.get(user, DEFAULT_BALANCE)
    await interaction.response.send_message(f"{interaction.user.mention}, your balance is: ${balance}")

@bot.tree.command(name="blackjack", description="Start a blackjack game")
async def slash_blackjack(interaction: discord.Interaction, bet: int):
    global blackjack_game
    user = str(interaction.user.id)
    player_money[user] = player_money.get(user, DEFAULT_BALANCE)

    if bet > player_money[user] or bet <= 0:
        embed = discord.Embed(title="Error", description="Insufficient funds or invalid bet amount!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    player_money[user] -= bet
    blackjack_game = Blackjack(bet)

    embed = discord.Embed(title="Blackjack Game Started!", color=discord.Color.blue())
    embed.add_field(name="Your Bet", value=f"${bet}", inline=False)
    embed.add_field(name="Your Hand", value=f"{blackjack_game.player_hand} (Total: {calculate_hand(blackjack_game.player_hand)})", inline=False)
    embed.add_field(name="Dealer Shows", value=blackjack_game.dealer_hand[0], inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="hit", description="Draw another card in blackjack")
async def slash_hit(interaction: discord.Interaction):
    global blackjack_game
    if not blackjack_game or blackjack_game.game_over:
        embed = discord.Embed(title="Error", description="No active game! Use /blackjack to start a new game.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    blackjack_game.hit(blackjack_game.player_hand)
    total = calculate_hand(blackjack_game.player_hand)

    if total > 21:
        blackjack_game.game_over = True
        embed = discord.Embed(title="Blackjack - Bust!", color=discord.Color.red())
        embed.add_field(name="Your Hand", value=f"{blackjack_game.player_hand} (Total: {total})", inline=False)
        embed.add_field(name="Result", value="You busted! Dealer wins.", inline=False)
    else:
        embed = discord.Embed(title="Blackjack - Hit", color=discord.Color.blue())
        embed.add_field(name="Your Hand", value=f"{blackjack_game.player_hand} (Total: {total})", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stand", description="Stand with your current hand in blackjack")
async def slash_stand(interaction: discord.Interaction):
    global blackjack_game
    if not blackjack_game or blackjack_game.game_over:
        embed = discord.Embed(title="Error", description="No active game! Use /blackjack to start a new game.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    blackjack_game.dealer_turn()
    blackjack_game.game_over = True
    result, money_change = blackjack_game.game_result()
    user = str(interaction.user.id)
    player_money[user] += money_change + blackjack_game.bet

    color = discord.Color.green() if money_change > 0 else discord.Color.red() if money_change < 0 else discord.Color.blue()

    embed = discord.Embed(title="Blackjack Result", color=color)
    embed.add_field(name="Dealer's Hand", value=f"{blackjack_game.dealer_hand} (Total: {calculate_hand(blackjack_game.dealer_hand)})", inline=False)
    embed.add_field(name="Result", value=result, inline=False)
    embed.add_field(name="New Balance", value=f"${player_money[user]}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tictactoe", description="Start a new Tic-Tac-Toe game")
async def slash_tictactoe(interaction: discord.Interaction):
    tictactoe_game.reset()
    embed = discord.Embed(title="Tic-Tac-Toe Game", color=discord.Color.blue())
    embed.add_field(name="Game Started!", value="Use /move <position> (0-8) to play.", inline=False)
    embed.add_field(name="Current Board", value=f"```{tictactoe_game.print_board()}```", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="move", description="Make a move in Tic-Tac-Toe (0-8)")
async def slash_move(interaction: discord.Interaction, position: int):
    if 0 <= position < 9:
        result = tictactoe_game.make_move(position)
        if result:
            await interaction.response.send_message(result + "\n" + tictactoe_game.print_board())
        else:
            await interaction.response.send_message(tictactoe_game.print_board())
    else:
        await interaction.response.send_message("Invalid position! Use a number between 0 and 8.")

@bot.tree.command(name="wordgame", description="Start a new word scramble puzzle")
async def slash_wordgame(interaction: discord.Interaction):
    await wordgame.start(interaction)

@bot.tree.command(name="guess", description="Make a guess for the word puzzle")
async def slash_guess(interaction: discord.Interaction, word: str):
    await wordgame.guess(interaction, word)

@bot.tree.command(name="hint", description="Get a hint for the current word puzzle")
async def slash_hint(interaction: discord.Interaction):
    await wordgame.hint(interaction)

@bot.tree.command(name="wordboard", description="Show word game leaderboard")
async def slash_wordboard(interaction: discord.Interaction):
    await wordgame.show_leaderboard(interaction)

@bot.tree.command(name="commands", description="Show all available commands")
async def slash_commands(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.dark_red())

    # Admin Commands
    embed.add_field(name="👑 Admin Only",
                    value="""
/addmoney <user> <amount> - Add money to user's balance
/endgiveaway <id> - End an active giveaway
/reroll <id> - Reroll giveaway winner
""",
                    inline=False)

    # Magic 8 Ball Commands
    embed.add_field(name="🎱 Magic 8 Ball",
                    value="""
/8b <question> - Ask the Magic 8 Ball a question
""",
                    inline=False)

    # Tic-Tac-Toe Commands
    embed.add_field(name="🎮 Tic-Tac-Toe",
                    value="""
/tictactoe - Start a new game
/move <0-8> - Make a move
""",
                    inline=False)

    # Blackjack Commands
    embed.add_field(name="🎲 Blackjack",
                    value="""
/balance - Check balance
/blackjack <bet> - Start game
/hit - Draw card
/stand - Stand hand
""",
                    inline=False)

    # Word Game Commands
    embed.add_field(name="📝 Word Game",
                    value="""
/wordgame - Start puzzle
/guess <word> - Make guess
/hint - Get hint
/wordboard - Show scores
""",
                    inline=False)

    await interaction.response.send_message(embed=embed)

@bot.command()
async def addmoney(ctx, user: discord.Member, amount: int):
    if str(ctx.author.id) not in ADMIN_IDS:
        embed = discord.Embed(title="Error", description="You don't have permission to use this command!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    target_id = str(user.id)
    player_money[target_id] = player_money.get(target_id, DEFAULT_BALANCE) + amount

    embed = discord.Embed(title="Money Added", color=discord.Color.green())
    embed.add_field(name="Target User", value=user.mention, inline=False)
    embed.add_field(name="Amount Added", value=f"${amount}", inline=False)
    embed.add_field(name="New Balance", value=f"${player_money[target_id]}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='8b')
async def magic_8ball(ctx, *, question: str):
    answer = magic8ball.get_answer(question)
    await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")

#Giveaway commands
@bot.command()
async def startgiveaway(ctx, duration: int, *, prize: str):
    giveaway_id = giveaway_system.create_giveaway(str(ctx.channel.id), prize, duration, str(ctx.author.id))
    embed = discord.Embed(title="🎉 Giveaway Started!", color=discord.Color.green())
    embed.add_field(name="Prize", value=prize, inline=False)
    embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
    embed.add_field(name="Giveaway ID", value=giveaway_id, inline=False)
    embed.add_field(name="How to Join", value="React with 🎉 to join!\nUse `$participants " + giveaway_id + "` to see who joined!", inline=False)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")
    
    # Wait for duration then end giveaway
    await asyncio.sleep(duration * 60)
    result = giveaway_system.end_giveaway(giveaway_id)
    if result:
        winner_mention = f"<@{result['winner']}>"
        await ctx.send(f"🎉 Congratulations {winner_mention}! You won: {result['prize']}")
    else:
        await ctx.send("No one joined the giveaway!")

@bot.command()
async def endgiveaway(ctx, giveaway_id: str):
    if str(ctx.author.id) not in ADMIN_IDS:
        await ctx.send("Only admins can end giveaways!")
        return
        
    result = giveaway_system.end_giveaway(giveaway_id)
    if result:
        winner_mention = f"<@{result['winner']}>"
        await ctx.send(f"🎉 Congratulations {winner_mention}! You won: {result['prize']}")
    else:
        await ctx.send("Giveaway not found or no participants!")

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    
    if str(reaction.emoji) == "🎉":
        message = reaction.message
        for giveaway_id, giveaway in giveaway_system.active_giveaways.items():
            if str(message.channel.id) == giveaway['channel_id']:
                if giveaway_system.join_giveaway(giveaway_id, str(user.id)):
                    await user.send(f"You have successfully joined the giveaway for {giveaway['prize']}!")

@bot.command()
async def reroll(ctx, giveaway_id: str):
    if str(ctx.author.id) not in ADMIN_IDS:
        await ctx.send("Only admins can reroll giveaways!")
        return
    
    result = giveaway_system.reroll_winner(giveaway_id)
    if result:
        winner_mention = f"<@{result['winner']}>"
        await ctx.send(f"🎉 New winner for {result['prize']}: {winner_mention}")
    else:
        await ctx.send("Giveaway not found or no participants!")

@bot.command()
async def participants(ctx, giveaway_id: str):
    participants = giveaway_system.get_participants(giveaway_id)
    if participants:
        embed = discord.Embed(title="🎉 Giveaway Participants", color=discord.Color.blue())
        embed.add_field(name="Giveaway ID", value=giveaway_id, inline=False)
        embed.add_field(name=f"Participants ({len(participants)})", value="\n".join([f"<@{p}>" for p in participants]) or "No participants yet", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Giveaway not found or no participants!")

@bot.command()
async def ghistory(ctx):
    history = giveaway_system.get_history()

@bot.command()
async def clearchat(ctx):
    if str(ctx.channel.id) == AI_CHAT_CHANNEL_ID:
        gemma_model.clear_history(str(ctx.author.id))
        await ctx.send("Chat history cleared!")
    if history:
        embed = discord.Embed(title="Recent Giveaways", color=discord.Color.gold())
        for entry in history:
            winner_mention = f"<@{entry['winner']}>" if entry['winner'] else "No winner"
            embed.add_field(
                name=entry['prize'],
                value=f"Winner: {winner_mention}\nParticipants: {len(entry['participants'])}",
                inline=False
            )
        await ctx.send(embed=embed)
    else:
        await ctx.send("No giveaway history yet!")


# Get Token and Run Bot
token = os.getenv("BOT_TOKEN")
if not token:
    print("Error: BOT_TOKEN environment variable not set!")
    exit(1)

try:
    bot.run(token)
except Exception as e:
    print(f"Error starting bot: {e}")