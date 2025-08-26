from IA_interfaze import ChessAI
import chess
from IA.Heuristica import Evaluator


class MinMaxChessAI(ChessAI):
    """
    Chess AI using Minimax with Alpha-Beta pruning.
    """

    def __init__(self, depth: int = 3):
        self.depth = depth
        self._nodes_searched = 0

    # ------------------ PUBLIC METHOD ------------------ #
    def select_move(self, board: chess.Board, color: chess.Color) -> chess.Move:
        """
        Select the best move for the given position using Minimax with Alpha-Beta pruning.
        """
        self._nodes_searched = 0
        best_score = float('-inf')
        best_move = None
        alpha, beta = float('-inf'), float('inf')

        for move in self._get_ordered_moves(board):
            board.push(move)
            score = self._minmax(board, self.depth - 1, alpha, beta, maximizing=False, color=color)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)  # update pruning window

        return best_move, self._nodes_searched

    # ------------------ CORE SEARCH ------------------ #
    def _minmax(self, board, depth, alpha, beta, maximizing, color) -> float:
        """
        Recursive minimax search with alpha-beta pruning.
        """
        if self._is_terminal(board, depth):
            return self._evaluate(board, color)

        self._nodes_searched += 1
        if maximizing:
            return self._maximize(board, depth, alpha, beta, color)
        else:
            return self._minimize(board, depth, alpha, beta, color)

    # ------------------ BRANCH HANDLERS ------------------ #
    def _maximize(self, board, depth, alpha, beta, color) -> float:
        max_eval = float('-inf')
        for move in self._get_ordered_moves(board):
            board.push(move)
            eval_score = self._minmax(board, depth - 1, alpha, beta, maximizing=False, color=color)
            board.pop()

            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)

            if beta <= alpha:
                break
        return max_eval

    def _minimize(self, board, depth, alpha, beta, color) -> float:
        min_eval = float('inf')
        for move in self._get_ordered_moves(board):
            board.push(move)
            eval_score = self._minmax(board, depth - 1, alpha, beta, maximizing=True, color=color)
            board.pop()

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)

            if beta <= alpha: 
                break
        return min_eval

    # ------------------ HELPERS ------------------ #
    def _is_terminal(self, board: chess.Board, depth: int) -> bool:
        """Check if search should stop (depth or game end)."""
        return depth == 0 or board.is_game_over()

    def _evaluate(self, board: chess.Board, color: chess.Color) -> float:
        """Evaluate board from the perspective of the given color."""
        score = Evaluator.evaluate_board(board)
        return score if color == chess.WHITE else -score

    def _get_ordered_moves(self, board: chess.Board):
        """Order moves to improve pruning (captures first)."""
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.is_capture(m), reverse=True)
        return moves
