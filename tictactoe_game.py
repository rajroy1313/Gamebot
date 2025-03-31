
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
            elif ' ' not in self.board:
                self.game_over = True
                return "It's a draw!"
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return None
        return "Invalid move. Try again."

    def check_winner(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                         (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in win_conditions:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != ' ':
                return True
        return False

    def reset(self):
        self.__init__()

    def end(self):
        self.game_over = True
        self.board = [' ' for _ in range(9)]
