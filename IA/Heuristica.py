from IA_interfaze import ChessAI
import chess
import random



class Evaluator:
	VAL = {
		chess.PAWN: 100, 
		chess.KNIGHT: 320, 
		chess.BISHOP: 330,
		chess.ROOK: 500, 
		chess.QUEEN: 900, 
		chess.KING: 0
	}
	MATE = 10000
	CHECK_BONUS = 25
	MOBILITY_W = 2  # peso por movida de diferencia (ajustable)
	
	# Tablas pieza-casilla (PST) simplificadas para blancas (A1=0 ... H8=63)
	# Fuertemente simplificadas; sirven como demostración.
	PST_PAWN = [
		0,  0,  0,  0,  0,  0,  0,  0,
		5, 10, 10,-20,-20, 10, 10,  5,
		5, -5, -5,  0,  0, -5, -5,  5,
		0,  0,  0, 20, 20,  0,  0,  0,
		5,  5, 10, 25, 25, 10,  5,  5,
		10, 10, 20, 30, 30, 20, 10, 10,
		50, 50, 50, 50, 50, 50, 50, 50,
		0,  0,  0,  0,  0,  0,  0,  0,
	]
	PST_KNIGHT = [
		-50,-40,-30,-30,-30,-30,-40,-50,
		-40,-20,  0,  0,  0,  0,-20,-40,
		-30,  0, 10, 15, 15, 10,  0,-30,
		-30,  5, 15, 20, 20, 15,  5,-30,
		-30,  0, 15, 20, 20, 15,  0,-30,
		-30,  5, 10, 15, 15, 10,  5,-30,
		-40,-20,  0,  5,  5,  0,-20,-40,
		-50,-40,-30,-30,-30,-30,-40,-50,
	]
	PST_BISHOP = [
		-20,-10,-10,-10,-10,-10,-10,-20,
		-10,  5,  0,  0,  0,  0,  5,-10,
		-10, 10, 10, 10, 10, 10, 10,-10,
		-10,  0, 10, 10, 10, 10,  0,-10,
		-10,  5,  5, 10, 10,  5,  5,-10,
		-10,  0,  5, 10, 10,  5,  0,-10,
		-10,  0,  0,  0,  0,  0,  0,-10,
		-20,-10,-10,-10,-10,-10,-10,-20,
	]
	PST_ROOK = [
		 0,  0,  5, 10, 10,  5,  0,  0,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		-5,  0,  0,  0,  0,  0,  0, -5,
		 5, 10, 10, 10, 10, 10, 10,  5,
		 0,  0,  0,  0,  0,  0,  0,  0,
	]
	PST_QUEEN = [
		-20,-10,-10, -5, -5,-10,-10,-20,
		-10,  0,  0,  0,  0,  0,  0,-10,
		-10,  0,  5,  5,  5,  5,  0,-10,
		-5,  0,  5,  5,  5,  5,  0, -5,
		0,  0,  5,  5,  5,  5,  0, -5,
		-10,  5,  5,  5,  5,  5,  0,-10,
		-10,  0,  5,  0,  0,  0,  0,-10,
		-20,-10,-10, -5, -5,-10,-10,-20,
	]
	PST_KING = [
		20, 30, 10,  0,  0, 10, 30, 20,
		20, 20,  0,  0,  0,  0, 20, 20,
		-10,-20,-20,-20,-20,-20,-20,-10,
		-20,-30,-30,-40,-40,-30,-30,-20,
		-30,-40,-40,-50,-50,-40,-40,-30,
		-30,-40,-40,-50,-50,-40,-40,-30,
		-30,-40,-40,-50,-50,-40,-40,-30,
		-30,-40,-40,-50,-50,-40,-40,-30,
	]
	
	PST = {
		chess.PAWN:   PST_PAWN,
		chess.KNIGHT: PST_KNIGHT,
		chess.BISHOP: PST_BISHOP,
		chess.ROOK:   PST_ROOK,
		chess.QUEEN:  PST_QUEEN,
		chess.KING:   PST_KING,
	}
	
	@classmethod
	def _material_pst(cls, board: chess.Board) -> int:
		score = 0
		for piece_type, base in cls.VAL.items():
			for sq in board.pieces(piece_type, chess.WHITE):
				score += base + cls.PST[piece_type][sq]
			for sq in board.pieces(piece_type, chess.BLACK):
				score -= base + cls.PST[piece_type][chess.square_mirror(sq)]
		return score
		
	@classmethod
	def _mobility(cls, board: chess.Board) -> int:
		# Diferencia de movilidad (blancas - negras)
		if board.turn == chess.WHITE:
			w = board.legal_moves.count()
			board.push(chess.Move.null())
			b = board.legal_moves.count()
			board.pop()
		else:
			b = board.legal_moves.count()
			board.push(chess.Move.null())
			w = board.legal_moves.count()
			board.pop()
		return cls.MOBILITY_W * (w - b)
		
	@staticmethod
	def _count_file_pawns(board: chess.Board, color) -> list:
		counts = [0]*8
		for sq in board.pieces(chess.PAWN, color):
			counts[chess.square_file(sq)] += 1
		return counts
		
	@classmethod
	def _pawn_structure(cls, board: chess.Board) -> int:
		score = 0
		# Dobles y aislados
		for color, sign in ((chess.WHITE, +1), (chess.BLACK, -1)):
			files = cls._count_file_pawns(board, color)
			# Dobles
			for c in files:
				if c > 1:
					score += sign * (-15 * (c - 1))
			# Aislados
			for f, c in enumerate(files):
				if c == 0:
					continue
				left = files[f-1] if f-1 >= 0 else 0
				right = files[f+1] if f+1 <= 7 else 0
				if left == 0 and right == 0:
					score += sign * (-15)  # penalización simple
					
		# Pasados (bonus por avance)
		passed_bonus = [0, 10, 20, 35, 60, 100, 180, 0]  # idx=rank (0..7)
		for sq in board.pieces(chess.PAWN, chess.WHITE):
			f = chess.square_file(sq)
			r = chess.square_rank(sq)
			blockers = []
			for df in (-1, 0, 1):
				ff = f + df
				if 0 <= ff < 8:
					for rr in range(r+1, 8):
						blockers.append(chess.square(ff, rr))
			if not any(board.piece_at(s) == chess.Piece(chess.PAWN, chess.BLACK) for s in blockers):
				score += passed_bonus[r]
		for sq in board.pieces(chess.PAWN, chess.BLACK):
			f = chess.square_file(sq)
			r = chess.square_rank(sq)
			blockers = []
			for df in (-1, 0, 1):
				ff = f + df
				if 0 <= ff < 8:
					for rr in range(0, r):
						blockers.append(chess.square(ff, rr))
			if not any(board.piece_at(s) == chess.Piece(chess.PAWN, chess.WHITE) for s in blockers):
				score -= passed_bonus[7-r]
		return score
		
	@classmethod
	def evaluate_board(cls, board: chess.Board) -> int:
		# Mate
		if board.is_checkmate():
			return -cls.MATE if board.turn == chess.WHITE else cls.MATE
		score = 0
		score += cls._material_pst(board)
		score += cls._mobility(board)
		score += cls._pawn_structure(board)
		if board.is_check():
			score += cls.CHECK_BONUS if board.turn == chess.BLACK else -cls.CHECK_BONUS
		return int(score)


class HeuristicChessAI(ChessAI):
    def select_move(self, board: chess.Board, color: chess.Color):
        best_score = None
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = Evaluator.evaluate_board(board, color)
            board.pop()
            if best_score is None or score > best_score:
                best_score = score
                best_move = move
        return best_move
