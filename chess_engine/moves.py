import string

__all__ = [
    'Move'
]


class Move:
    rank_to_rows = {k: v for k, v in zip([str(i) for i in range(1, 9)], [i for i in range(8)][::-1])}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}

    files_to_cols = {k: v for k, v in zip([i for i in string.ascii_lowercase[:8]], [i for i in range(8)])}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant=False):

        self.start_row, self.start_col = start_sq
        self.end_row, self.end_col = end_sq

        self.move_id = self.start_row * 100 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (
                                         self.piece_moved == 'wP' and self.end_row == 0) or (
                                         self.piece_moved == 'bP' and self.end_row == 7
                                 )

        self.is_enpassant_move = is_enpassant
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
