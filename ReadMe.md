# Chess IA - Documentación

## ¿Qué puede hacer este programa?

Este programa permite simular partidas de ajedrez entre diferentes agentes de Inteligencia Artificial (IA) y/o un jugador humano. Las funcionalidades principales incluyen:

- Jugar partidas de ajedrez en dos modos:
  - **Persona vs Máquina (PvAI):** El usuario juega contra una IA.
  - **Máquina vs Máquina (AIvAI):** Dos agentes IA juegan entre sí.
- Visualización del tablero en consola con piezas Unicode.
- Registro y exportación de la partida en formato PGN.
- Gráficas de nodos analizados por jugada para comparar el rendimiento de las IA.
- Soporte para diferentes agentes IA: Random, Heurística, MinMax, Negamax, Monte Carlo Tree Search.

---

## ¿Cómo se ejecuta?

1. Instala las dependencias necesarias:
   ```bash
   pip install python-chess matplotlib
   ```

2. Ejecuta el programa desde la terminal:
   ```bash
   python main.py
   ```
   O, si tienes varias versiones de Python:
   ```bash
   python3 main.py
   ```

3. Selecciona el modo de juego cuando se te solicite:
   - Opción 1: Persona vs Máquina
   - Opción 2: Máquina vs Máquina

4. Juega o observa la partida. Al finalizar, se exporta el archivo `partida.pgn` y se muestra una gráfica de nodos analizados por jugada.

---

## Resultados

- El resultado de la partida se muestra al final (victoria, empate, jaque mate).
- Se genera un archivo PGN con la partida jugada.
- Se muestra una gráfica comparando la cantidad de nodos analizados por cada IA en cada jugada, útil para analizar el rendimiento y profundidad de búsqueda de los agentes.

---

## Ejemplo de uso básico

```python
# main.py
if __name__ == '__main__':
    ai_white = MonteCarloTreeSearchAI(n_simulations=3000)
    ai_black = NegamaxChessAI(depth=3)
    main()
```

---

## Explicación detallada de cada agente IA

### 1. RandomChessAI

**Descripción:** Selecciona un movimiento legal al azar.

**Ejemplo de uso:**
```python
# IA/Random.py
class RandomChessAI:
    def select_move(self, board: chess.Board, color: chess.Color):
        """Devuelve un movimiento elegido al azar entre los legales.

        - board: objeto python-chess con la posición actual.
        - color: color que está por mover (blancas/negras).
        """
        moves = list(board.legal_moves)  # listar movimientos legales
        # si no hay movimientos (jaque mate o tablas), devolvemos None
        if not moves:
            return None
        # elegimos uno al azar y lo devolvemos
        return random.choice(moves)
```

**Ventajas:** Muy rápido, útil como baseline.
**Desventajas:** No tiene estrategia, juega movimientos aleatorios.

---

### 2. HeuristicChessAI

**Descripción:** Evalúa los movimientos legales usando una función heurística (por ejemplo, valor de piezas, control de centro, etc.) y elige el mejor según esa evaluación.

Estas heuristicas son muy utiles debido a que nos permite tener una forma de evaluar la calides de una posicion y poder dar valores numericos a ramas en futuros algoritmos sin necesidad de llegar a su estado terminal

Esta heuristica se compone de varios factores:
- La calidad de la pieza
- La ventaja posicional de una pieza y su posicion en el table
- Estructura de tables
- Si es mate, tabla o jacke, se da un valor extra (si es mate, se da un infinito matematico)

**Ejemplo de uso:**
```python
# IA/Heuristica.py
class HeuristicChessAI:
    def select_move(self, board: chess.Board, color: chess.Color):
        best_score = float('-inf')
        best_move = None
        # Recorremos todos los movimientos legales
        for move in board.legal_moves:
            board.push(move)              # aplicar movimiento (stack)
            score = self.evaluate(board)  # calcular heurística en la nueva posición
            board.pop()                   # restaurar posición original

            # Si la evaluación es mejor que la mejor conocida, actualizamos
            if score > best_score:
                best_score = score
                best_move = move

        # devolvemos el movimiento con mejor evaluación
        return best_move

    def evaluate(self, board: chess.Board):
        # Ejemplo de combinación de factores (normalizar y sumar):
        #  - material (centipawns)
        #  - movilidad (nº movimientos legales)
        #  - seguridad del rey (penalizar enroques perdidos)
        #  - bonus por mates detectados
        # Implementa aquí tu función existente: debe devolver un valor en centipawns.
        pass
```

**Fragmento de código típico:**
```python
# IA/Min_Max.py
class MinMaxChessAI:
    def select_move(self, board: chess.Board, color: chess.Color):
        # minmax: funcion recursiva que devuelve la evaluación desde la perspectiva del jugador 'color_to_move'
        def minmax(board, depth, maximizing_player):
            # condición de corte: profundidad 0 o posición terminal
            if depth == 0 or board.is_game_over():
                return self.evaluate(board)

            if maximizing_player:
                max_eval = float('-inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minmax(board, depth - 1, False)
                    board.pop()
                    max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = float('inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minmax(board, depth - 1, True)
                    board.pop()
                    min_eval = min(min_eval, eval)
                return min_eval

        # Selección del mejor movimiento: probamos cada movimiento y evaluamos
        best_move = None
        best_score = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            score = minmax(board, self.depth - 1, False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move
```

**Ventajas:** Juega de forma más inteligente que Random, considerando factores básicos del ajedrez.
**Desventajas:** No planifica a futuro, solo evalúa el estado actual.

---

### 3. MinMaxChessAI

**Descripción:** Implementa el algoritmo MinMax, explorando posibles movimientos hasta una cierta profundidad y eligiendo el movimiento que maximiza el resultado propio y minimiza el del oponente.

**Ejemplo de uso:**
```python
from IA.Min_Max import MinMaxChessAI
ai = MinMaxChessAI(depth=3)
move, nodos = ai.select_move(board, color)
```

**Fragmento de código típico:**
```python
# IA/Min_Max.py
class MinMaxChessAI:
    def select_move(self, board: chess.Board, color: chess.Color):
        # minmax: funcion recursiva que devuelve la evaluación desde la perspectiva del jugador 'color_to_move'
        def minmax(board, depth, maximizing_player):
            # condición de corte: profundidad 0 o posición terminal
            if depth == 0 or board.is_game_over():
                return self.evaluate(board)

            if maximizing_player:
                max_eval = float('-inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minmax(board, depth - 1, False)
                    board.pop()
                    max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = float('inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minmax(board, depth - 1, True)
                    board.pop()
                    min_eval = min(min_eval, eval)
                return min_eval

        # Selección del mejor movimiento: probamos cada movimiento y evaluamos
        best_move = None
        best_score = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            score = minmax(board, self.depth - 1, False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move
```

**Ventajas:** Considera varios turnos hacia adelante, puede jugar tácticamente.
**Desventajas:** El rendimiento depende de la profundidad; puede ser lento si la profundidad es alta.

---

### 4. NegamaxChessAI

**Descripción:** Variante del MinMax, simplifica la lógica usando simetría entre jugadores. Puede incluir poda alfa-beta para optimizar la búsqueda.

Explicar tambien el hasing utilizado aqui

**Ejemplo de uso:**
```python
from IA.NegaMax import NegamaxChessAI
ai = NegamaxChessAI(depth=3)
move, nodos = ai.select_move(board, color)
```

**Fragmento de código típico:**
```python
# IA/NegaMax.py
class NegamaxChessAI:
    def __init__(self, depth=3):
        self.depth = depth
        self.transposition_table = {}  # Zobrist hash -> (value, depth, flag, best_move)
        self._init_zobrist()          # inicializa tabla Zobrist (valores aleatorios)

    def negamax(self, board, depth, alpha, beta, color):
        key = self._zobrist_hash(board)
        # 1) consulta tabla de transposición (si existe y es válida)
        if key in self.transposition_table:
            value, stored_depth, flag, best_move = self.transposition_table[key]
            # flag indica si value es exacto, o es un bound (LOWER/UPPER)
            if stored_depth >= depth:
                if flag == 'EXACT':
                    return value
                if flag == 'LOWER':
                    alpha = max(alpha, value)
                elif flag == 'UPPER':
                    beta = min(beta, value)
                if alpha >= beta:
                    return value

        # 2) caso terminal o profundidad 0 -> evaluar
        if depth == 0 or board.is_game_over():
            return color * self.evaluate(board)  # 'color' = +1 para max, -1 para min

        max_eval = float('-inf')
        best_move_local = None
        for move in board.legal_moves:
            board.push(move)
            eval = -self.negamax(board, depth - 1, -beta, -alpha, -color)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move_local = move
            alpha = max(alpha, eval)
            if alpha >= beta:
                break  # poda alfa-beta

        # 3) almacenar en tabla de transposición con flag adecuado
        # flag = 'EXACT' / 'LOWER' / 'UPPER' según alpha/beta
        self.transposition_table[key] = (max_eval, depth, 'EXACT', best_move_local)
        return max_eval
```

**Ventajas:** Más eficiente que MinMax, especialmente con poda alfa-beta.
**Desventajas:** Similar a MinMax, pero más rápido en posiciones complejas.

---

### 5. MonteCarloTreeSearchAI

**Descripción:** Realiza simulaciones aleatorias desde el estado actual y construye un árbol de búsqueda basado en los resultados de esas simulaciones. Elige el movimiento con mejor expectativa.

**Ejemplo de uso:**
```python
from IA.MonteCarloTreeSearch import MonteCarloTreeSearchAI
ai = MonteCarloTreeSearchAI(n_simulations=1000)
move = ai.select_move(board, color)
```

**Fragmento de código típico:**
```python
# IA/MonteCarloTreeSearch.py
class MonteCarloTreeSearchAI:
    def select_move(self, board, color):
        for _ in range(self.n_simulations):
            # Simulación aleatoria desde el estado actual
            # Actualización de estadísticas del árbol
            pass
        # Selección del movimiento con mejor expectativa
        return best_move
```

**Ventajas:** Muy potente en posiciones abiertas, puede encontrar jugadas inesperadas.
**Desventajas:** Requiere muchas simulaciones para ser efectivo, puede ser lento si el número de simulaciones es alto.

---

## Personalización de agentes

Puedes cambiar los agentes en el archivo `main.py`:
```python
# Ejemplo para usar MCTS como IA blanca o negra:
ai_white = MonteCarloTreeSearchAI(n_simulations=100)
ai_black = MinMaxChessAI(depth=3)
```

---

## Créditos

- Basado en [python-chess](https://python-chess.readthedocs.io/)
- Autor: JhojanZ

---
