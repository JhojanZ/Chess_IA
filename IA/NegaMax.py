from IA_interfaze import ChessAI
import chess
from IA.Heuristica import Evaluator


class NegamaxChessAI(ChessAI):
    """
    Chess AI using Negamax with Alpha-Beta pruning.
    """

    def __init__(self, depth: int = 3):
        self.depth = depth
        self.transposition_table = {}
        self._nodes_searched = 0
        self._init_zobrist()

    # ------------------ PUBLIC METHOD ------------------ #
    def select_move(self, board: chess.Board, color: chess.Color) -> chess.Move:
        """
        Select the best move for the given position using Negamax with Alpha-Beta pruning.
        """
        self._nodes_searched = 0
        best_score = float('-inf')
        best_move = None
        alpha, beta = float('-inf'), float('inf')

        # Convención: color = +1 si son blancas, -1 si son negras
        player_color = 1 if color == chess.WHITE else -1

        for move in self._get_ordered_moves(board):
            board.push(move)
            score = -self.negamax(board, self.depth - 1, -beta, -alpha, -player_color)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)  # update pruning window

        return best_move, self._nodes_searched

    def negamax(self, board, depth, alpha, beta, color):
        self._nodes_searched += 1
        zobrist_key = self.transposition_key(board)

        # Buscar en la Transposition Table
        if zobrist_key in self.transposition_table:
            entry_depth, entry_score = self.transposition_table[zobrist_key]
            if entry_depth >= depth:
                return entry_score

        # Caso base
        if depth == 0 or board.is_game_over():
            score = color * self._evaluate(board)
            self.transposition_table[zobrist_key] = (depth, score)
            return score

        max_eval = -float("inf")
        for move in board.legal_moves:
            board.push(move)
            score = -self.negamax(board, depth - 1, -beta, -alpha, -color)
            board.pop()

            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        self.transposition_table[zobrist_key] = (depth, max_eval)
        return max_eval

    def _init_zobrist(self):
        import random
        random.seed(42)  # opcional: fija la semilla
        self._zobrist_table = {}
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        for sq in range(64):
            for piece in pieces:
                self._zobrist_table[(piece, sq)] = random.getrandbits(64)
        self._zobrist_table['turn'] = random.getrandbits(64)
        for cr in ['K', 'Q', 'k', 'q']:
            self._zobrist_table[cr] = random.getrandbits(64)
        for sq in range(64):
            self._zobrist_table[('ep', sq)] = random.getrandbits(64)

    def transposition_key(self, board: chess.Board):
        """Devuelve una clave única para el tablero actual usando Zobrist hashing personalizado."""
        # Inicializar la tabla Zobrist si no existe
        
        h = 0
        # Piezas en el tablero
        for sq in range(64):
            piece = board.piece_at(sq)
            if piece:
                h ^= self._zobrist_table[(piece.symbol(), sq)]
        # Turno
        if board.turn == chess.WHITE:
            h ^= self._zobrist_table['turn']
        # Enroques
        if board.has_kingside_castling_rights(chess.WHITE):
            h ^= self._zobrist_table['K']
        if board.has_queenside_castling_rights(chess.WHITE):
            h ^= self._zobrist_table['Q']
        if board.has_kingside_castling_rights(chess.BLACK):
            h ^= self._zobrist_table['k']
        if board.has_queenside_castling_rights(chess.BLACK):
            h ^= self._zobrist_table['q']
        # Peón al paso
        if board.ep_square is not None:
            h ^= self._zobrist_table[('ep', board.ep_square)]
        return h

    # ------------------ HELPERS ------------------ #
    def _evaluate(self, board: chess.Board) -> float:
        """Evaluate board always from White's perspective."""
        return Evaluator.evaluate_board(board)

    def _get_ordered_moves(self, board: chess.Board):
        """Order moves to improve pruning (captures first)."""
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        return moves
