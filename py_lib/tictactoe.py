class TicTacToe:
    def __init__(self, player_x, player_o):
        self.player_x = player_x
        self.player_o = player_o
        self.current_turn_is_o = False  # False for X, True for O
        self.x_board = 0
        self.o_board = 0
        self.turns = 0

    @property
    def board(self):
        return self.x_board | self.o_board

    @property
    def current_turn(self):
        return self.player_o if self.current_turn_is_o else self.player_x

    @staticmethod
    def check(state):
        # Winning combinations in bitmask form
        win_combos = [7, 56, 73, 84, 146, 273, 292, 448]
        for combo in win_combos:
            if (state & combo) == combo:
                return True
        return False

    @staticmethod
    def to_binary(x=0, y=0):
        if not (0 <= x <= 2 and 0 <= y <= 2):
            raise ValueError('Invalid position')
        return 1 << (x + 3 * y)

    def turn(self, player_is_o, pos_or_x, y=None):
        if self.board == 511:  # Board is full
            return -3

        pos = 0
        if y is None:
            if not (0 <= pos_or_x <= 8):
                return -1  # Invalid position
            pos = 1 << pos_or_x
        else:
            if not (0 <= pos_or_x <= 2 and 0 <= y <= 2):
                return -1 # Invalid Position
            pos = self.to_binary(pos_or_x, y)

        if self.current_turn_is_o != player_is_o:
            return -2  # Not your turn

        if self.board & pos:
            return 0  # Position occupied

        if self.current_turn_is_o:
            self.o_board |= pos
        else:
            self.x_board |= pos

        self.current_turn_is_o = not self.current_turn_is_o
        self.turns += 1
        return 1

    @staticmethod
    def render_board(board_x=0, board_o=0):
        board = []
        for i in range(9):
            pos = 1 << i
            if board_x & pos:
                board.append('X')
            elif board_o & pos:
                board.append('O')
            else:
                board.append(str(i + 1))
        return board

    def render(self):
        return self.render_board(self.x_board, self.o_board)

    @property
    def winner(self):
        if self.check(self.x_board):
            return self.player_x
        if self.check(self.o_board):
            return self.player_o
        return None
