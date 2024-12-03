# CMPUT 455 Assignment 4 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a4.html

import sys
import random
import signal
import math
import time

# Custom time out exception
class TimeoutException(Exception):
    pass

# Function that is called when we reach the time limit
def handle_alarm(signum, frame):
    raise TimeoutException

class TreeNode:
    def __init__(self, board, parent=None, move=None):
        self.board = [row[:] for row in board]  # Deep copy the board
        self.parent = parent
        self.children = []
        self.move = move
        self.visits = 0
        self.score = 0

    def is_fully_expanded(self):
        legal_moves = self.parent.get_legal_moves() if self.parent else []
        return len(self.children) == len(legal_moves)

    def best_child(self, exploration_weight=1.41):
        if not self.children:
            return None
        return max(self.children, key=lambda child:
            child.score / max(1, child.visits) + exploration_weight *
            math.sqrt(math.log(max(1, self.visits)) / max(1, child.visits)))

# Main command interface
class CommandInterface:

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner,
            "timelimit": self.timelimit
        }
        self.board = [[None]]
        self.player = 1
        self.max_genmove_time = 1
        signal.signal(signal.SIGALRM, handle_alarm)
    
    #====================================================================================================================
    # VVVVVVVVVV Start of predefined functions. You may modify, but make sure not to break the functionality. VVVVVVVVVV
    #====================================================================================================================



    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    def game(self, args):
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False
        
        self.board = []
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        return True
    
    def show(self, args):
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()                    
        return True

    def is_legal(self, x, y, num):
        if self.board[y][x] is not None:
            return False, "occupied"
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        too_many = count > len(self.board) // 2 + len(self.board) % 2
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False, "too many " + str(num)

        self.board[y][x] = None
        return True, ""
    
    def valid_move(self, x, y, num):
        if  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1):
            legal, _ = self.is_legal(x, y, num)
            return legal

    def play(self, args):
        try:
            if len(args) != 3:
                raise ValueError(f"Wrong number of arguments: {args}")

            x = int(args[0])
            y = int(args[1])
            num = int(args[2])

            if x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
                raise ValueError(f"Wrong coordinate: {x}, {y}")
            if num not in [0, 1]:
                raise ValueError(f"Wrong number: {num}")

            legal, reason = self.is_legal(x, y, num)
            if not legal:
                raise ValueError(f"Illegal move: {reason}")

            self.board[y][x] = num
            self.player = 3 - self.player  # Switch between players
            return True

        except ValueError as e:
            print(f"= illegal move: {' '.join(args)} {e}\n", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error in play method: {e}", file=sys.stderr)
            return False
    
    def legal(self, args):
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True

    def get_legal_moves(self):
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    legal, _ = self.is_legal(x, y, num)
                    if legal:
                        moves.append([str(x), str(y), str(num)])
        if not moves:
            print("DEBUG: No legal moves available", file=sys.stderr)
        else:
            print(f"DEBUG: Found {len(moves)} legal moves", file=sys.stderr)
        return moves

    def winner(self, args):
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True

    def timelimit(self, args):
        try:
            self.max_genmove_time = max(5, int(args[0]))  # Minimum 5 seconds
            print(f"DEBUG: Time limit set to {self.max_genmove_time} seconds", file=sys.stderr)
            return True
        except ValueError:
            print("ERROR: Invalid time limit argument", file=sys.stderr)
            return False

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of predefined functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV Start of Assignment 4 functions. Add/modify as needed. VVVVVVVV
    #===============================================================================================

    def mcts(self, board, max_iterations=1000):
        import time
        start_time = time.time()
        root = TreeNode(board)
        iterations = 0

        while iterations < max_iterations:
            # Time check
            elapsed_time = time.time() - start_time
            if elapsed_time >= self.max_genmove_time - 1:  # Leave 1 second buffer
                print(f"DEBUG: Time limit reached after {elapsed_time:.2f} seconds", file=sys.stderr)
                break

            # Selection
            node = self.select(root)

            # Expansion
            if not node.is_fully_expanded():
                node = self.expand(node)

            # Simulation
            result = self.simulate(node.board)

            # Backpropagation
            self.backpropagate(node, result)
            iterations += 1

        print(f"DEBUG: MCTS completed {iterations} iterations", file=sys.stderr)
        best_move = root.best_child(exploration_weight=0).move if root.children else None
        return best_move

    def select(self, node):
        while node.is_fully_expanded() and node.children:
            node = node.best_child()
        return node

    def expand(self, node):
        legal_moves = self.get_legal_moves()
        if not legal_moves:
            print("DEBUG: No legal moves in expand", file=sys.stderr)
            return node

        for move in legal_moves:
            if move not in [child.move for child in node.children]:
                new_board = [row[:] for row in node.board]
                x, y, num = map(int, move)
                new_board[y][x] = num
                child_node = TreeNode(new_board, parent=node, move=move)
                node.children.append(child_node)
                print(f"DEBUG: Expanded move {move}", file=sys.stderr)
                return child_node

        print("DEBUG: Node already fully expanded", file=sys.stderr)
        return node

    def simulate(self, board, max_depth=20):
        current_board = [row[:] for row in board]
        player = self.player
        depth = 0

        while depth < max_depth:
            legal_moves = self.get_legal_moves()
            if not legal_moves:
                print("DEBUG: No legal moves left during simulation", file=sys.stderr)
                break
            move = random.choice(legal_moves)
            x, y, num = map(int, move)
            current_board[y][x] = num
            player = 3 - player  # Switch player
            depth += 1

        return self.evaluate_board(current_board, self.player)

    def backpropagate(self, node, result):
        while node:
            node.visits += 1
            if result == self.player:  # Win
                node.score += 1
            elif result == 3 - self.player:  # Loss
                node.score -= 1
            node = node.parent

    def heuristic_move(self, board, player):
        legal_moves = self.get_legal_moves()
        best_score = -float('inf')
        best_move = random.choice(legal_moves)  # Default to a random move

        for move in legal_moves:
            x, y, num = map(int, move)
            # Simulate the move
            board[y][x] = num
            score = self.evaluate_board(board, player)
            board[y][x] = None  # Undo the move

            # Choose the move with the highest score
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def evaluate_board(self, board, player):
        opponent = 3 - player
        score = 0

        # Rows, columns, and diagonals evaluation
        for y in range(len(board)):
            score += self.evaluate_line(board[y], player, opponent)
        for x in range(len(board[0])):
            column = [board[y][x] for y in range(len(board))]
            score += self.evaluate_line(column, player, opponent)

        diagonals = [
            [board[i][i] for i in range(min(len(board), len(board[0])))],
            [board[i][len(board[0]) - 1 - i] for i in range(min(len(board), len(board[0])))],
        ]
        for diag in diagonals:
            score += self.evaluate_line(diag, player, opponent)

        return score

    def evaluate_line(self, line, player, opponent):
        player_score = line.count(player)
        opponent_score = line.count(opponent)
        return player_score - opponent_score

    def genmove(self, args):
        try:
            import time
            start_time = time.time()

            signal.alarm(self.max_genmove_time)
            print(f"DEBUG: Starting genmove for player {self.player}", file=sys.stderr)

            # Determine the best move using MCTS
            best_move = self.mcts(self.board, max_iterations=1000)

            # Play the selected move or resign if no move found
            if best_move:
                self.play(best_move)
                print(f"DEBUG: Best move chosen: {best_move}", file=sys.stderr)
            else:
                print("resign")
                print("DEBUG: No valid move found, resigning", file=sys.stderr)

            signal.alarm(0)
            elapsed_time = time.time() - start_time
            print(f"DEBUG: genmove completed in {elapsed_time:.2f} seconds", file=sys.stderr)

        except TimeoutException:
            print("resign")
            print("DEBUG: genmove timeout occurred", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Exception in genmove: {e}", file=sys.stderr)
            print("resign")
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()