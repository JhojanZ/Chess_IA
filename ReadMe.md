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
from IA.Random import RandomChessAI
ai = RandomChessAI()
move = ai.select_move(board, color)
```

**Ventajas:** Muy rápido, útil como baseline.
**Desventajas:** No tiene estrategia, juega movimientos aleatorios.

---

### 2. HeuristicChessAI

**Descripción:** Evalúa los movimientos legales usando una función heurística (por ejemplo, valor de piezas, control de centro, etc.) y elige el mejor según esa evaluación.

**Ejemplo de uso:**
```python
from IA.Heuristica import HeuristicChessAI
ai = HeuristicChessAI()
move = ai.select_move(board, color)
```

**Fragmento de código típico:**
```python
# IA/Heuristica.py
class HeuristicChessAI:
    def select_move(self, board, color):
        best_score = float('-inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = self.evaluate(board)
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
    def select_move(self, board, color):
        def minmax(board, depth, maximizing):
            if depth == 0 or board.is_game_over():
                return self.evaluate(board)
            if maximizing:
                max_eval = float('-inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minmax(board, depth-1, False)
                    board.pop()
                    max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = float('inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval = minmax(board, depth-1, True)
                    board.pop()
                    min_eval = min(min_eval, eval)
                return min_eval
        # Selección del mejor movimiento
        best_move = None
        best_score = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            score = minmax(board, self.depth-1, False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move, nodos_evaluados
```

**Ventajas:** Considera varios turnos hacia adelante, puede jugar tácticamente.
**Desventajas:** El rendimiento depende de la profundidad; puede ser lento si la profundidad es alta.

---

### 4. NegamaxChessAI

**Descripción:** Variante del MinMax, simplifica la lógica usando simetría entre jugadores. Puede incluir poda alfa-beta para optimizar la búsqueda.

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
    def select_move(self, board, color):
        def negamax(board, depth, alpha, beta, color):
            if depth == 0 or board.is_game_over():
                return color * self.evaluate(board)
            max_eval = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                eval = -negamax(board, depth-1, -beta, -alpha, -color)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break  # Poda alfa-beta
            return max_eval
        # Selección del mejor movimiento
        best_move = None
        best_score = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            score = -negamax(board, self.depth-1, float('-inf'), float('inf'), -1)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move, nodos_evaluados
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
