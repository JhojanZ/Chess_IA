
import sys
import chess
import chess.pgn

from IA.Random import RandomChessAI
from IA.Heuristica import HeuristicChessAI
from IA.Min_Max import MinMaxChessAI
from IA.NegaMax import NegamaxChessAI

# Unicode chess pieces mapping for python-chess
PIECES = {
    chess.PAWN: {'w': '\u2659', 'b': '\u265F'},
    chess.KNIGHT: {'w': '\u2658', 'b': '\u265E'},
    chess.BISHOP: {'w': '\u2657', 'b': '\u265D'},
    chess.ROOK:   {'w': '\u2656', 'b': '\u265C'},
    chess.QUEEN:  {'w': '\u2655', 'b': '\u265B'},
    chess.KING:   {'w': '\u2654', 'b': '\u265A'},
}

def print_board(board: chess.Board):
    print('  a b c d e f g h')
    for rank in range(8, 0, -1):
        print(rank, end=' ')
        for file in range(8):
            square = chess.square(file, rank-1)
            piece = board.piece_at(square)
            if piece:
                print(PIECES[piece.piece_type][piece.color and 'w' or 'b'], end=' ')
            else:
                print(' ', end=' ')
        print(rank)
    print('  a b c d e f g h')

def get_user_move(board: chess.Board, color: chess.Color):
    legal_moves = list(board.legal_moves)
    print('Movimientos disponibles:')
    print(legal_moves)
    while True:
        user_input = input('Introduce tu movimiento (ej: e2e4): ')
        try:
            move = chess.Move.from_uci(user_input)
            if move in legal_moves:
                return move
        except Exception:
            pass
        print('Movimiento inválido. Intenta de nuevo.')

def exportar_pgn(board: chess.Board, filename: str = "partida.pgn"):
    game = chess.pgn.Game.from_board(board)
    with open(filename, "w", encoding="utf-8") as f:
        print(game, file=f, end="\n")

def main():
    mode = None
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print('Selecciona modo:')
        print('1. Persona vs Maquina')
        print('2. Maquina vs Maquina')
        sel = input('Opción (1/2): ')
        mode = 'pvai' if sel == '1' else 'aivai'

    board = chess.Board()

    while not board.is_game_over():
        print_board(board)
        color = board.turn
        if mode == 'pvai' and color == chess.WHITE:
            move = get_user_move(board, color)
        else:
            ai = ai_white if color == chess.WHITE else ai_black
            move = ai.select_move(board, color)
            if move is None:
                print('No hay movimientos legales disponibles. Juego terminado.')
                break
            print(f"Maquina ({'blancas' if color == chess.WHITE else 'negras'}) mueve: {board.san(move)} ({move.uci()})")
        board.push(move)
    print_board(board)
    print('Fin de la partida:', board.result(), "   ", board.is_checkmate())
    exportar_pgn(board)

if __name__ == '__main__':
    #ai = RandomChessAI()
    #ai = HeuristicChessAI()
    #ai_white = MinMaxChessAI(depth=5)
    #ai_black = MinMaxChessAI(depth=5)
    ai_white = NegamaxChessAI(depth=5)
    ai_black = NegamaxChessAI(depth=5)
    main()
