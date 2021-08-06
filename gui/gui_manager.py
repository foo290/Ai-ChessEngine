from chess_engine import GameState, Move
import pygame
import os
from .ui_effects import Colors
from typing import List
from logger.logger import get_custom_logger

log = get_custom_logger("ChessEngine")

__all__ = [
    "GuiManager"
]


class GuiManager:
    WIDTH = HEIGHT = 780
    DIMENSIONS = 8
    SQ_SIZE = HEIGHT // DIMENSIONS

    MAX_FPS = 15
    IMAGES = {}

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.pieces = [
            'wR', 'wN', 'wB', 'wQ', 'wK', 'wP',
            'bR', 'bN', 'bB', 'bQ', 'bK', 'bP'
        ]
        self.pieces_dir = 'chessPieces/'

        self.move_made = False
        self.animate = False
        self.running = True
        self.game_over = False
        self.default_board_clr = [Colors.WHITE, Colors.DARK_BLACK]
        self.board_clr = self.default_board_clr

    def set_board_color(self, color: List[Colors]):
        self.board_clr = color

    def load_images(self):
        for piece in self.pieces:
            self.IMAGES[piece] = pygame.transform.scale(
                pygame.image.load(
                    os.path.join(self.pieces_dir, f"{piece}.png")), (self.SQ_SIZE, self.SQ_SIZE)
            )

    def highlight_move(self, game_state: GameState, valid_move, square_selected):
        if square_selected:
            r, c = square_selected

            if game_state.board[r][c][0] == ('w' if game_state.white_move else 'b'):
                s = pygame.Surface((self.SQ_SIZE, self.SQ_SIZE))
                s.set_alpha(50)
                s.fill(pygame.Color('blue'))
                self.screen.blit(s, (c * self.SQ_SIZE, r * self.SQ_SIZE))

                s.fill(pygame.Color('green'))
                for move in valid_move:
                    if move.start_row == r and move.start_col == c:
                        self.screen.blit(s, (move.end_col * self.SQ_SIZE, move.end_row * self.SQ_SIZE))

    def draw_text(self, text):
        font = pygame.font.SysFont("Helvetica", 32, True, False)
        text_object = font.render(text, False, pygame.Color((255, 89, 223)))

        text_loc = pygame.Rect(
            0, 0, self.WIDTH, self.HEIGHT).move(
            self.WIDTH / 2 - text_object.get_width() / 2,
            self.HEIGHT / 2 - text_object.get_height() / 2
        )

        self.screen.blit(text_object, text_loc)

    def draw_game_state(self, game_state, valid_move, square_selected):
        self.draw_board()
        self.highlight_move(game_state, valid_move, square_selected)
        self.draw_pieces(game_state.board)

    def draw_board(self):

        for r in range(self.DIMENSIONS):
            for c in range(self.DIMENSIONS):
                color = self.board_clr[(r + c) % 2]
                pygame.draw.rect(
                    self.screen, color, pygame.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
                )

    def draw_pieces(self, board):
        for r in range(self.DIMENSIONS):
            for c in range(self.DIMENSIONS):
                piece = board[r][c]
                if piece != '--':
                    self.screen.blit(
                        self.IMAGES[piece], pygame.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)
                    )

    def animate_move(self, move, board, clock):
        dr = move.end_row - move.start_row
        dc = move.end_col - move.start_col

        fps = 5
        frame_count = (abs(dr) + abs(dc)) * fps

        for frame in range(frame_count + 1):
            r, c = (move.start_row + dr * frame / frame_count, move.start_col + dc * frame / frame_count)
            self.draw_board()
            self.draw_pieces(board)
            end_sq = pygame.Rect(move.end_col * self.SQ_SIZE, move.end_row * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE)

            pygame.draw.rect(self.screen, pygame.Color('white'), end_sq)
            if move.piece_captured != '--':
                self.screen.blit(self.IMAGES[move.piece_captured], end_sq)

            self.screen.blit(self.IMAGES[move.piece_moved],
                             pygame.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
            pygame.display.flip()
            clock.tick(60)

    def run_main_loop(self):
        self.load_images()
        valid_moves = self.game_state.get_valid_moves()

        square_selected = ()  # row and col
        player_clicks = []  # have two tuples, where user clicks

        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

                # mouse events
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_over:
                        loc = pygame.mouse.get_pos()
                        log.debug(f"Click detected at : {loc}")

                        col = loc[0] // self.SQ_SIZE
                        row = loc[1] // self.SQ_SIZE

                        if square_selected == (row, col):
                            # if player place piece at its own location
                            log.error("Invalid Move!, Location was same as initial. Resetting state.")
                            square_selected = ()
                            player_clicks = []
                        else:
                            square_selected = (row, col)
                            player_clicks.append(square_selected)

                        if len(player_clicks) == 2:
                            move = Move(player_clicks[0], player_clicks[1], self.game_state.board)

                            if move in valid_moves:
                                log.info("Move is valid.")
                                log.info(f'Piece Moved : {move.get_chess_notation()}')
                                log.info(f"TURN : {'White' if self.game_state.white_move else 'Black'}")

                                # game_state.make_move(valid_moves[valid_moves.index(move)])

                                self.game_state.make_move(move)
                                self.animate = self.move_made = True
                                square_selected = ()
                                player_clicks = []
                            else:
                                player_clicks = [square_selected]

                # key events
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_z:
                        log.warning("Executing undo request for last move...") if \
                            self.game_state.undo_last_move() else log.error("Undo requested but there is no last moves")
                        self.move_made = True
                        self.animate = False

                    if e.key == pygame.K_r:  # Reset the game
                        game_state = GameState()
                        valid_moves = game_state.get_valid_moves()
                        square_selected = ()
                        player_clicks = []
                        self.move_made = self.animate = False

            if self.move_made:
                if self.animate:
                    self.animate_move(self.game_state.move_logs[-1], self.game_state.board, self.clock)
                valid_moves = self.game_state.get_valid_moves()
                log.debug("Move was made, generating next moves...")
                self.move_made = self.animate = False

            self.draw_game_state(self.game_state, valid_moves, square_selected)

            if self.game_state.check_mate:
                self.game_over = True
                if self.game_state.white_move:
                    self.draw_text("Black wins")
                else:
                    self.draw_text("white wins")
            elif self.game_state.stale_mate:
                self.game_over = True
                self.draw_text("Stale mate")

            self.clock.tick(self.MAX_FPS)
            pygame.display.flip()
