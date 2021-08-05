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


def highlight_move(screen, gs: chess_engine.GameState, valid_move, square_selected):
    if square_selected:
        r, c = square_selected

        if gs.board[r][c][0] == ('w' if gs.white_move else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(50)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            s.fill(pygame.Color('green'))
            for move in valid_move:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def animate_move(move, screen, board, clock):
    dr = move.end_row - move.start_row
    dc = move.end_col - move.start_col

    fps = 5

    frame_count = (abs(dr) + abs(dc)) * fps
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dr * frame / frame_count, move.start_col + dc * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        end_sq = pygame.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

        pygame.draw.rect(screen, pygame.Color('white'), end_sq)
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_sq)

        screen.blit(IMAGES[move.piece_moved], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game_state = chess_engine.GameState()
    load_images()

    valid_moves = game_state.get_valid_moves()
    move_made = False
    animate = False
    running = True
    game_over = False

    square_selected = ()  # row and col
    player_clicks = []  # have two tuples, where user clicks

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            # mouse events
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
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

                            # game_state.make_move(valid_moves[valid_moves.index(move)])

                            game_state.make_move(move)
                            animate = move_made = True
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
                    animate = False

                if e.key == pygame.K_r:  # Reset the game
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = animate = False

        if move_made:
            if animate:
                animate_move(game_state.move_logs[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            log.debug("Move was made, generating next moves...")
            # log.debug(f"next moves: {valid_moves}")
            move_made = animate = False

        draw_game_state(screen, game_state, valid_moves, square_selected)

        if game_state.check_mate:
            game_over = True
            if game_state.white_move:
                draw_text(screen, "Black wins")
            else:
                draw_text(screen, "white wins")
        elif game_state.stale_mate:
            game_over = True
            draw_text(screen, "Stale mate")

        clock.tick(MAX_FPS)
        pygame.display.flip()

def draw_text(screen, text):
    font = pygame.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, pygame.Color((255, 89, 223)))
    text_loc = pygame.Rect(0,0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2-text_object.get_height()/2)
    screen.blit(text_object, text_loc)



def draw_game_state(screen, game_state, valid_move, square_selected):
    draw_board(screen)
    highlight_move(screen, game_state, valid_move, square_selected)
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
