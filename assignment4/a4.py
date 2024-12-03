# CMPUT 455 Assignment 4 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a4.html

import sys
import random
import signal
import numpy as np
import math
import os

# Custom time out exception
class TimeoutException(Exception):
    pass

class ZobristHashing():

    def __init__(self, x_dim, y_dim):
        self.x_dim = x_dim
        self.y_dim = y_dim

    def random_int(self):
        min = 0
        max = pow(2,64)
        return random.randint(min,max)
    
    def indexOf(self,piece):
        if (piece==0):
            return 0
        elif (piece==1):
            return 1
        else:
            return -1
    
    def initTable(self):
        
        num_item_to_place_on_board = 2
        ZobristTable = [[[self.random_int() for k in range(num_item_to_place_on_board)] for j in range(self.y_dim)] for i in range (self.x_dim)]
        return ZobristTable
    
    def computeHash(self, game_board, ZobristTable):
        h = 0
        for i in range(self.x_dim):
            for j in range(self.y_dim):
                if (game_board[j][i] != None):
                    piece = self.indexOf(game_board[j][i])
                    h ^= ZobristTable[i][j][piece]
        return h

class Patterns():

    def __init__(self):
        self.patterns = {}
        self.loadpatterns()
    
    def loadpatterns(self):
        # script_directory = os.path.dirname(os.path.abspath(__file__))
        script_directory = os.getcwd()
        filename = script_directory+"/"+'fullpattern.txt'
        self.patterns.clear()
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith ("#"):
                    continue # Skip empty lines and comments
                parts = line.split()
                pattern = parts[0]
                move = int (parts [1])
                weight = int(parts [2])
                if pattern not in self.patterns:
                    self.patterns[pattern] = {}
                self.patterns[pattern][move]= weight

    def generate_policy_probabilities(self, list_of_legal_moves, board_state):
        legal_moves = sorted(list_of_legal_moves, key=lambda x: (x[0], x[1], x[2]))

        unratioed_moves = []
        #ratioed moves is the one with probabilties to be used for the policy
        ratioed_moves = []
        sum_of_all_weights = 0


        for legal_move in legal_moves:
            x_axis = int(legal_move[0])
            y_axis = int(legal_move[1])
            move = int(legal_move[2])

            row_pattern = self.make_pattern(x_axis,y_axis,0, board_state)
            # print("Row Pattern: " + row_pattern)

            column_pattern = self.make_pattern(x_axis,y_axis,1, board_state)
            # print("Column Pattern: " + column_pattern)

            row_flipped = row_pattern[::-1]
            column_flipped = column_pattern[::-1]
            
            # print("ROW: {} AND FLIPPED {}: ".format(row_pattern,row_flipped))
            # print("COLUMN: {} AND FLIPPED {}: ".format(column_pattern,column_flipped))

            #check if pattern and its axis-counterparts are in self.patterns

            move
            row = [row_pattern, row_flipped]
            column = [column_pattern, column_flipped]

            total_weight = 0

            # when pattern is not in self.patterns, give a default of 10
            hit = False
            default = 10
            for item in row:
                if(item in self.patterns):
                    total_weight += self.patterns[item][move]
                    hit=True

            if(not hit):
                total_weight += default

            hit = False
            for item in column:
                if(item in self.patterns):
                    total_weight += self.patterns[item][move]
                    hit=True
                    
            if(not hit):
                total_weight += default

            unratioed_item = [x_axis, y_axis, move, total_weight]
            sum_of_all_weights += total_weight
            unratioed_moves.append(unratioed_item)

        for item in unratioed_moves:
            new_item = [item[0],item[1],item[2],item[3]/sum_of_all_weights]
            ratioed_moves.append(new_item)
        
        return ratioed_moves

    def make_pattern(self,x_axis,y_axis,boolean,board):
        """
            if boolean is 0, return the row pattern
            if boolean is 1, return the column pattern
        """

        if(boolean == 1):
            temp = x_axis
            x_axis = y_axis
            y_axis = temp

        five_pattern = ""

        #left or up side of the pattern even when its not square
        for i in range(2):
            current_x = x_axis-2+i
            if((current_x)<0):
                five_pattern = five_pattern+"X"
            else:
                
                if(boolean):
                    item = board[current_x][y_axis]
                else:
                    item = board[y_axis][current_x]

                if (item == None):
                    item = '.'
                five_pattern = five_pattern+str(item)
        five_pattern = five_pattern + "."

        #right or down side of the pattern
        if boolean == 0:
            limit = len(board[0])
        else:
            limit = len(board)
        for i in range(2):
            current_x = x_axis+(i+1)
            if((current_x)>=limit):
                five_pattern = five_pattern+"X"
            else:

                if(boolean):
                    item = board[current_x][y_axis]
                else:
                    item = board[y_axis][current_x]

                if (item == None):
                    item = '.'
                five_pattern = five_pattern+str(item)

        return five_pattern

class MyNode():
    
    def __init__(self, game, state, move_made=None, parent=None,):
        self.game = game
        self.state = state
        self.parent = parent
        self.move_made = move_made

        self.children = []
        self.wins = 0
        self.score = None

    def expand(self):
        """
            This does not play any move, rather, a node object with the move TO BE MADE is created
            which keeps the board state unchanged.

            The list of the node objects are returned.
        """
        childrenNodes = []
        legal_moves = self.game.get_legal_moves()
        for legal_move in legal_moves:
            
            childNode = MyNode(self.game, self.state, move_made=legal_move, parent= self)
            childrenNodes.append(childNode)

        self.children = childrenNodes    

    def get_children(self):
        return self.children
    
    def set_score(self, score):
        self.score = score

    def playMove(self):
        self.game.play(self.move_made)

class TranspositionTable():

    def __init__(self):
        self.transposition_table = {}

    def update_TranspositionTable(self, hash, score):

        self.transposition_table[hash] = score

    def get_equivalent_score(self, hash):
        
        return self.transposition_table[hash]

    def contains(self, hash_value):

        return hash_value in self.transposition_table

    def initialize_symmetries(self, board):
        
        pass

class FlatMC():
    
    def __init__(self, game, simulation_count=1, custom_policy=None):    
        self.game = game
        self.simulation_count = simulation_count
        self.custom_policy = custom_policy
        self.hasher = ZobristHashing(len(self.game.board[0]),len(self.game.board))
        self.table = self.hasher.initTable()

    def run_algorithm(self):

        initial_board_state = self.game.create_board_copy()
        root_node = MyNode(self.game, initial_board_state)

        root_node.expand() #initializes the children nodes
        childrenNodes = root_node.get_children()
        t_table = TranspositionTable()

        if len(childrenNodes) > 18:
            self.simulation_count = 100
        else:
            self.simulattion_count = 1000

        for childNode in childrenNodes:
            childNode.playMove()
            #IF Transposition Table contains the childnode equivalent
            hash = self.hasher.computeHash(self.game.board, self.table)
            if t_table.contains(hash):
                
                #Fetch the score and assign it
                score = t_table.get_equivalent_score(hash)
                childNode.set_score(score)
            else:
            #Otherwise, play the move, simulate from the move then compute the score
                score = self.simulate_and_score()
                childNode.set_score(score)
                #Then, place all the symmetries to the transposition table
                
                t_table.update_TranspositionTable(hash,score)
                flip_board = self.game.board
                
                for i in range(2):
                    flip_board = self.flip(flip_board,'horizontal')
                    hash = self.hasher.computeHash(flip_board, self.table)
                    t_table.update_TranspositionTable(hash,score)

                    flip_board = self.flip(flip_board,'vertical')
                    hash = self.hasher.computeHash(flip_board, self.table)
                    t_table.update_TranspositionTable(hash,score)
                
                self.reset_board(initial_board_state)
                
                #invert the value of move
                move = childNode.move_made
                inverted_move = move[:]
                if inverted_move[2] == '0':
                    inverted_move[2] = '1'
                else:
                    inverted_move[2] = '0'

                legal, _ = self.game.is_legal(int(inverted_move[0]),int(inverted_move[1]),int(inverted_move[2]))

                if legal:
                    self.game.play(inverted_move)

                    flip_board = self.game.board
                    for i in range(2):
                        flip_board = self.flip(flip_board,'horizontal')
                        hash = self.hasher.computeHash(flip_board, self.table)
                        t_table.update_TranspositionTable(hash,score)

                        flip_board = self.flip(flip_board,'vertical')
                        hash = self.hasher.computeHash(flip_board, self.table)
                        t_table.update_TranspositionTable(hash,score)

            self.reset_board(initial_board_state) 

        sorted_objects = sorted(childrenNodes, key=lambda obj: obj.score, reverse=True) 

        return sorted_objects[0].move_made           

    def simulate_and_score(self):
        """
        Simulates a run from start to a terminal state and tallies wins
        """
        board_state_from_node = self.game.create_board_copy()
        wins = 0
        for i in range(self.simulation_count):
            while self.game.is_terminal() == False:
                move = self.get_move_from_policy('RULE')
                self.game.play(move)        
            if self.check_win() == 1:
                wins += 1

            self.reset_board(board_state_from_node)

        return wins/self.simulation_count

    def reset_board(self, target_state):
        self.game.board = []
        for row in target_state:
            self.game.board.append(list(row))

    def flip(self, board, axis):
        """
            axis is 0 for horizontal and 1 for vertical
        """

        if axis == 'horizontal':
        # Reverse the rows (flip along the horizontal axis)
            return board[::-1]
        elif axis == 'vertical':
            # Reverse the columns in each row (flip along the vertical axis)
            return [row[::-1] for row in board]

    def invert(self, board):
        pass

    def expand(self, node: MyNode):
        node.expand()

    def get_random_move(self):
        movelist = self.game.get_legal_moves()
        random.shuffle(movelist)
        random_move = movelist[0]
        return random_move

    def get_educated_move(self):
        movelist = self.game.get_legal_moves()
        data = self.custom_policy.generate_policy_probabilities(movelist, self.game.board)

        cumulative = []
        total = 0
        for item in data:
            total += item[3]
            cumulative.append(total)

        # Pick based on random number
        rand_val = random.uniform(0, 1)
        for i, threshold in enumerate(cumulative):
            if rand_val <= threshold:
                picked = data[i]
                break

        move_as_string = [str(x) for x in picked[:-1]]

        return move_as_string

    def get_move_from_policy(self, args):
        """default policy is random"""
        if args == 'RAND' or args == None:
            
            return self.get_random_move()
            
        elif args == 'RULE':
            
            return self.get_educated_move()
        
    def check_win(self):
        if len(self.game.get_legal_moves()) == 0:
            if self.game.player == 1:
                return 2
            else:
                return 1

# Function that is called when we reach the time limit
def handle_alarm(signum, frame):
    raise TimeoutException

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
        self.max_genmove_time = 30
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
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        return True
    
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
        self.max_genmove_time = int(args[0])
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of predefined functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV Start of Assignment 4 functions. Add/modify as needed. VVVVVVVV
    #===============================================================================================
    
    def is_terminal(self):
        return len(self.get_legal_moves()) == 0

    def genmove(self, args):
        
        try:
            # Set the time limit alarm
            signal.alarm(self.max_genmove_time)
            
            # Modify the following to give better moves than random play 
            moves = self.get_legal_moves()
            if len(moves) == 0:
                print("resign")
            else:

                #---------------------------------
                move_found = self.run_move_algorithm()
                #---------------------------------
                # rand_move = moves[random.randint(0, len(moves)-1)]
                self.play(move_found)
                print(" ".join(move_found))
            
            # Disable the time limit alarm 
            signal.alarm(0)

        except TimeoutException:
            # This block of code runs when the time limit is reached
            print("resign")

        return True
    
    def run_move_algorithm(self):
        board_copy = self.create_board_copy()
        simulation_count = 1000
        custom_policy = Patterns()
        flatMC = FlatMC(self, simulation_count, custom_policy)
        return flatMC.run_algorithm()

    def create_board_copy(self):
        board_copy = []
        for row in self.board:
            board_copy.append(list(row))
        return board_copy
        
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ End of Assignment 4 functions. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()