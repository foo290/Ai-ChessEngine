import string
from typing import List

from logger.logger import get_custom_logger

log = get_custom_logger("CHESS-ENGINE")


class GameState:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.white_move = True
        self.move_logs: List[Move] = []

        self.move_generator_map = {
            'P': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }

        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)

        self.check_mate = False
        self.stale_mate = False

    def is_empty(self, r, c):
        return self.board[r][c] == '--'

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved

        self.move_logs.append(move)

        if move.piece_moved == 'wK':
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)

        self.white_move = not self.white_move

    def undo_last_move(self):
        if self.move_logs:
            last_move = self.move_logs.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            self.white_move = not self.white_move
            return True

    def get_valid_moves(self):
        """ considering checks """
        moves = self.get_possible_moves()

        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])

            self.white_move = not self.white_move
            if self.in_check():
                moves.remove(moves[i])

            self.white_move = not self.white_move
            self.undo_last_move()

        if len(moves) == 0:
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.stale_mate = self.check_mate = False

        return moves

    def in_check(self):
        if self.white_move:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, r, c):
        self.white_move = not self.white_move
        opponent_moves = self.get_possible_moves()

        self.white_move = not self.white_move
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def get_possible_moves(self):
        """ without considering checks """
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_move) or (turn == 'b' and not self.white_move):
                    piece = self.board[r][c][1]
                    self.move_generator_map[piece](r, c, moves)

        # log.debug(f"valid Moves: {moves}")
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_move:
            if self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                if c + 1 <= 7:
                    if self.board[r - 1][c + 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                if c + 1 <= 7:
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def get_knight_moves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = 'b' if self.white_move else 'w'

        for m in knightMoves:
            end_row = r + m[0]
            end_col = c + m[1]

            if 0 <= end_row < 8 and 0 < end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color or end_piece == '--':
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_king_moves(self, r, c, moves):
        king_moves = (
            (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        )
        ally_color = 'w' if self.white_move else 'b'

        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_clr = "b" if self.white_move else "w"

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_clr:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        # firendly piece
                        break
                else:
                    break


class Move:
    rank_to_rows = {k: v for k, v in zip([str(i) for i in range(1, 9)], [i for i in range(8)][::-1])}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}

    files_to_cols = {k: v for k, v in zip([i for i in string.ascii_lowercase[:8]], [i for i in range(8)])}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, startSQ, endSQ, board):
        self.start_row, self.start_col = startSQ
        self.end_row, self.end_col = endSQ

        self.move_id = self.start_row * 100 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + " -> " + self.get_rank_file(self.end_row,
                                                                                                self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id

    def __str__(self):
        return f"{self.get_chess_notation()}"

    def __repr__(self):
        return f"{self.get_chess_notation()}"


print(Move.rows_to_ranks)
