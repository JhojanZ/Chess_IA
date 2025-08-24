from IA_interfaze import ChessAI
import chess
import random


class RandomChessAI(ChessAI):
    def select_move(self, board: chess.Board, color: chess.Color):
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None