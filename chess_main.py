import chess_engine
import pygame
from logger.logger import get_custom_logger

log = get_custom_logger("ChessEngine")

WIDTH = HEIGHT = 780
DIMENSIONS = 8
SQ_SIZE = HEIGHT // DIMENSIONS

MAX_FPS = 15
IMAGES = {}


def load_images():
    pieces = [
        'wR', 'wN', 'wB', 'wQ', 'wK', 'wP',
        'bR', 'bN', 'bB', 'bQ', 'bK', 'bP'
    ]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load('chessPieces/' + piece + '.png'), (SQ_SIZE, SQ_SIZE)
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game_state = chess_engine.GameState()
    load_images()

    valid_moves = game_state.get_valid_moves()
    move_made = False

    running = True

    square_selected = ()  # row and col
    player_clicks = []  # have two tuples, where user clicks

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            # mouse events
            elif e.type == pygame.MOUSEBUTTONDOWN:
                loc = pygame.mouse.get_pos()
                log.debug(f"Click detected at : {loc}")

                col = loc[0] // SQ_SIZE
                row = loc[1] // SQ_SIZE

                if square_selected == (row, col):
                    # if player place piece at its own location
                    log.error("Invalid Move!, Location was same as initial. Resetting state.")
                    square_selected = ()
                    player_clicks = []
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)

                if len(player_clicks) == 2:
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], game_state.board)

                    if move in valid_moves:
                        log.info("Move is valid.")
                        log.info(f'Piece Moved : {move.get_chess_notation()}')
                        log.info(f"TURN : {'White' if game_state.white_move else 'Black'}")
                        game_state.make_move(move)
                        move_made = True
                        square_selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [square_selected]


            # key events
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    log.warning("Executing undo request for last move...") if \
                        game_state.undo_last_move() else log.error("Undo requested but there is no last moves")

                    move_made = True

        if move_made:
            valid_moves = game_state.get_valid_moves()
            log.debug("Move was made, generating next moves...")
            # log.debug(f"next moves: {valid_moves}")
            move_made = False

        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        pygame.display.flip()


def draw_game_state(screen, game_state):
    draw_board(screen)
    draw_pieces(screen, game_state.board)


def draw_board(screen):
    colors = [pygame.Color((140, 140, 140)), pygame.Color((79, 79, 79))]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


main()
