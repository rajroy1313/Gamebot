
#!/bin/bash

print_title() {
    echo "=== Discord Bot Commands ==="
    echo ""
}

print_tic_tac_toe() {
    echo "Tic-Tac-Toe Commands:"
    echo "$start - Start a new Tic-Tac-Toe game"
    echo "$move <0-8> - Make a move in Tic-Tac-Toe"
    echo "$reset - Reset the Tic-Tac-Toe game"
    echo "$end - End the Tic-Tac-Toe game"
    echo ""
}

print_blackjack() {
    echo "Blackjack Commands:"
    echo "$balance - Check your current balance"
    echo "$blackjack <bet> - Start a blackjack game with a bet"
    echo "$hit - Draw another card in blackjack"
    echo "$stand - Stand with your current hand in blackjack"
    echo ""
}

print_word_game() {
    echo "Word Game Commands:"
    echo "$wordgame - Start a new word scramble puzzle"
    echo "$guess <word> - Make a guess for the current word puzzle"
    echo "$hint - Get a hint for the current word puzzle"
    echo "$wordboard - Show word game leaderboard"
    echo ""
}

print_utility() {
    echo "Utility Commands:"
    echo "$commands - Show this list of commands"
}

# Main execution
print_title
print_tic_tac_toe
print_blackjack
print_word_game
print_utility
