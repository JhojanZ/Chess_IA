from IA_interfaze import ChessAI
import chess
import random
import math
from IA.Heuristica import Evaluator

class MCTSNode:
    def __init__(self, board, parent=None, move=None, zobrist_hash=None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.hash = zobrist_hash


    def is_fully_expanded(self):
        return len(self.children) == len(list(self.board.legal_moves))

    def best_child(self, c_param=1.4):
        choices_weights = [
            (child.wins / child.visits) + c_param * ( (math.log(self.visits) / child.visits) ** 0.5 )
            if child.visits > 0 else float('inf')
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]
    
    


class MonteCarloTreeSearchAI(ChessAI):
    def __init__(self, n_simulations=100):
        self.n_simulations = n_simulations
        self.transposition_table = {}
        self._init_zobrist()
        self.top_n = 3  # número de mejores movimientos a considerar en cada simulación
        self._nodes_searched = 0

    def select_move(self, board: chess.Board, color: chess.Color):
        self._nodes_searched = 0
        root = MCTSNode(board)
        for _ in range(self.n_simulations):
            self._nodes_searched += 1
            node = root
            # Selection
            while node.children and node.is_fully_expanded():
                node = node.best_child()
            # Expansion
            if not node.board.is_game_over():
                legal_moves = list(node.board.legal_moves)
                tried_moves = [child.move for child in node.children]
                for move in legal_moves:
                    if move not in tried_moves:
                        new_board = node.board.copy()
                        new_board.push(move)
                        new_hash = self.transposition_key(new_board)

                        if new_hash in self.transposition_table:
                            child_node = self.transposition_table[new_hash]
                            child_node.parent = node  # enlazar al nuevo padre
                            # ⚠️ Resetear stats al reutilizar
                            child_node.visits = 0
                            child_node.wins = 0
                        else:
                            child_node = MCTSNode(new_board, parent=node, move=move, zobrist_hash=new_hash)
                            self._nodes_searched += 1
                            self.transposition_table[new_hash] = child_node

                        node.children.append(child_node)
                        node = child_node
                        break
            # Simulation
            # Simulation usando heurística
            sim_board = node.board.copy()
            max_depth = 30  # límite de jugadas a simular para no ir tan profundo
            depth = 0

            while not sim_board.is_game_over() and depth < max_depth:
                moves = list(sim_board.legal_moves)
                moves.sort(key=lambda m: sim_board.is_capture(m), reverse=True)
                candidate_moves = moves[:min(self.top_n, len(moves))]
                move = random.choice(candidate_moves)
                sim_board.push(move)
                depth += 1

            if sim_board.is_game_over():
                # Si terminó la partida, recompensa clásica
                result = sim_board.result()
                reward = self._get_reward(result, color)
            else:
                # Si llegamos al límite, usamos la heurística de Evaluator
                score = Evaluator.evaluate_board(sim_board)
                # Normalizamos score a [0,1] para que sea compatible con backprop
                reward = 1 / (1 + pow(10, -score/800))
  # tipo fórmula Elo/logística
            # Backpropagation
            while node:
                node.visits += 1
                if node.board.turn == color:
                    node.wins += reward
                else:
                    node.wins += 1 - reward
                node = node.parent

        # Choose best move
        if not root.children:
            return None
        best = max(root.children, key=lambda c: c.visits)

        # I'm tired, just check and select the first best move possible
        # This is return some good move but of past position, i have clear the cache somehow
        if best.move not in board.legal_moves:
            # fallback: elegir otro hijo válido
            valid_children = [c for c in root.children if c.move in board.legal_moves]
            if valid_children:
                best = max(valid_children, key=lambda c: c.visits)
            else:
                return random.choice(list(board.legal_moves)) if board.legal_moves else None
        return best.move, self._nodes_searched

    def _get_reward(self, result, color):
        if result == '1-0':
            return 1 if color == chess.WHITE else 0
        elif result == '0-1':
            return 1 if color == chess.BLACK else 0
        else:
            return 0.5

    def _init_zobrist(self):
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