import string
from typing import List

from logger.logger import get_custom_logger

log = get_custom_logger("CHESS-ENGINE")

ylog = log.ylog
glog = log.glog
blog = log.blog
rlog = log.rlog
clog = log.clog


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

        self.enpassant_possible = ()  # coord where enpassant capture is possible

    def is_empty(self, r, c):
        return self.board[r][c] == '--'

    def get_player_clr(self):
        return "White" if self.white_move else "Black"

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved

        self.move_logs.append(move)
        self.white_move = not self.white_move

        if move.piece_moved == 'wK':
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)

        # Pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # EnPassant Move
        if move.is_enpassant_move:
            clog("Move is EnPassednt Move", 'enpassant')
            self.board[move.start_row][move.end_col] = '--'

        # update enPassant var
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            glog(f"Updating enpassant var to {(move.start_row + move.end_row) // 2, move.start_col}")
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            glog("Resetting enpassant")
            self.enpassant_possible = ()

    def undo_last_move(self):
        if self.move_logs:
            last_move = self.move_logs.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
            self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
            self.white_move = not self.white_move

            if last_move.piece_moved == 'wK':
                self.white_king_loc = (last_move.start_row, last_move.start_col)
            elif last_move.piece_moved == 'bK':
                self.black_king_loc = (last_move.start_row, last_move.start_col)

            # undo enPassant move
            if last_move.is_enpassant_move:
                self.board[last_move.end_row][last_move.end_col] = '--'
                self.board[last_move.start_row][last_move.end_col] = last_move.piece_captured
                self.enpassant_possible = (last_move.end_row, last_move.end_col)
            # undo a 2 square pawn
            if last_move.piece_moved[1] == 'P' and abs(last_move.start_row - last_move.end_row) == 2:
                self.enpassant_possible = ()

            return True

    def get_valid_moves(self):
        """ considering checks """
        tempEnPassantPossible = self.enpassant_possible

        ylog(f"Getting valid moves for {self.get_player_clr()}")
        moves = self.get_possible_moves()

        ylog(f"{len(moves)} possible moves")

        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])

            self.white_move = not self.white_move
            if self.in_check():
                ylog(f"Move : {moves[i]} leaving king in check, removing this move from valid moves...")
                moves.remove(moves[i])

            self.white_move = not self.white_move
            self.undo_last_move()

        if len(moves) == 0:
            ylog("NO VALID MOVES LEFT, Checking game state...")
            if self.in_check():
                rlog("CHECK MATE!")
                self.check_mate = True
            else:
                rlog("STALE MATE!")
                self.stale_mate = True
        else:
            self.stale_mate = self.check_mate = False

        self.enpassant_possible = tempEnPassantPossible
        ylog(f"{len(moves)} valid moves")
        return moves

    def in_check(self):
        if self.white_move:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, r, c):
        self.white_move = not self.white_move
        ylog("Getting Opponent's moves...")
        opponent_moves = self.get_possible_moves()
        ylog(f"Opponent moves are : {len(opponent_moves)}")

        self.white_move = not self.white_move
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                clog(f"Move: {move} leaving square in check, returning true.")
                return True
        rlog("Opponent can not attack king, returning false")
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
                elif (r - 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassant=True))

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassant=True))

        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassant=True))

                if c + 1 <= 7:
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enpassant_possible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassant=True))

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

    def __init__(self, startSQ, endSQ, board, isEnpassant=False):

        self.start_row, self.start_col = startSQ
        self.end_row, self.end_col = endSQ

        self.move_id = self.start_row * 100 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (
                                         self.piece_moved == 'wP' and self.end_row == 0) or (
                                         self.piece_moved == 'bP' and self.end_row == 7
                                 )

        self.is_enpassant_move = isEnpassant
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

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

# print(Move.rows_to_ranks)
