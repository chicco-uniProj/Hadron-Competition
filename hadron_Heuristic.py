import game
import math

# Hadron Game
# The moves of player have the form (y,x), where y is the column number and x the row number (starting with 0)
# In the visualization, they are in the form (row, column) starting with 1.

# If it receives - 1 as the number of moves, then the game is finished

infinity = math.inf

def playerStrategy (conn,game,qO):
    state = game.initial
    newState = state
    number_of_moveRec = 0

    move = None

    inizioIo=False
    cutOffGiocosecondo=False
    cutoff = 0
    passo_cutoff = 7


    while not game.is_terminal(state):
        (number_of_moveRec, newState) = conn.recv()
        while conn.poll():
            (number_of_moveRec, newState) = conn.recv()
        if number_of_moveRec == -1:
            return

        if newState != None:

            """
            print("Controlli:")
            print(number_of_moveRec)
            print(inizioIo)
            print(passo_cutoff)
            """
            if(number_of_moveRec%2!=0 and not inizioIo):
                inizioIo=True

            if(not inizioIo and not cutOffGiocosecondo):
                cutoff=1
                cutOffGiocosecondo=True

            #print(inizioIo and number_of_moveRec != 0 and passo_cutoff != 0 and (number_of_moveRec + 1) % passo_cutoff == 0)

            if (not inizioIo and number_of_moveRec!=0 and passo_cutoff!=0 and number_of_moveRec % passo_cutoff == 0):
                cutoff += 1
                if passo_cutoff > 3:
                    passo_cutoff -= 2

            elif(inizioIo and number_of_moveRec!=0 and passo_cutoff!=0 and (number_of_moveRec+1) % passo_cutoff == 0):
                cutoff += 1
                if passo_cutoff > 3:
                    passo_cutoff -= 1

            #print("Mossa: " , number_of_moveRec, "cutoff = ", cutoff)
            # In this example, O plays with alphabetaSearch
            value, move = h_alphabeta_search(game, newState, cutoff%2== 1,cutoff_depth(cutoff))

            #print("value = ", value)

            #print("---------------------------------------------------------------")
            
            conn.send((number_of_moveRec, newState, move))
            qO.put((number_of_moveRec, move))
            
            state = newState

    return

def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d


def h_alphabeta_search(game, state, reverse, cutoff=cutoff_depth(2)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache1
    def max_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            h_value = heuristic(state, state.to_move, game)
            if reverse:
                 return -h_value, None
            else:
                 return h_value, None

        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache1
    def min_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):

            h_value = heuristic(state, state.to_move, game)
            if reverse:
                 return -h_value, None
            else:
                 return h_value, None

        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)

def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}
    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped

def heuristic(board, player, game):
    num_moves = len(game.actions(board))
    opponent = "X" if player == "O" else "O"
    score = 0
    for i in range(9):
        for j in range(9):
            if board[i,j] == player:
                # controlla le adiacenze orizzontali e verticali
                if i > 0 and board[i - 1,j] == opponent:
                    score += 0.2
                if i < 9 - 1 and board[i + 1,j] == opponent:
                    score += 0.2
                if j > 0 and board[i,j - 1] == opponent:
                    score += 0.2
                if j < 9 - 1 and board[i,j + 1] == opponent:
                    score += 0.2
                # controlla le adiacenze diagonalmente
                if i > 0 and j > 0 and board[i - 1,j - 1] == opponent:
                    score += 0.1
                if i > 0 and j < 9 - 1 and board[i - 1,j + 1] == opponent:
                    score += 0.1
                if i < 9 - 1 and j > 0 and board[i + 1,j - 1] == opponent:
                    score += 0.1
                if i < 9 - 1 and j < 9 - 1 and board[i + 1,j + 1] == opponent:
                    score += 0.1


    # aggiungi un bonus se il numero di mosse effettuate Ã¨ dispari
    if num_moves % 2 == 0:
        score += 0.6
    else:
        score -= 0.6

    # normalizza il valore della funzione euristica tra -1 e 1
    return 2 * score / (9 ** 2) - 1
