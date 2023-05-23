from utils import Trie
import numpy as np
import multiprocessing as mp
import tkinter as tk

class SpellCastSolver():
    def __init__(self, board):
        self.board = np.array(board)

        self.word_search = Trie()

        words = open("words.txt", "r").read().split("\n")
        for word in words:
            self.word_search.insert(word)

        self.directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1)
        ]
        self.directions = [np.array(direction) for direction in self.directions]

        self.letter_values = np.array([1, 4, 5, 3, 1, 5, 3, 4, 1, 7, 3, 3, 4, 2, 1, 4, 8, 2, 2, 2, 4, 5, 5, 7, 4, 8])

        self.upper_bound = np.array((4, 4))
        self.lower_bound = np.array((0, 0))

    def _get_location_value(self, location):
        value = self.letter_values[ord(self.board[location]) - ord('a')]
        # todo : add a modifier here
        return value
    
    def _get_path_value(self, path):
        return sum([self._get_location_value(location) for location in path])
    
    def _get_word_value(self, word):
        return sum([self.letter_values[ord(i) - ord('a')] for i in word])

    def set_board(self, board):
        self.board = np.array(board)

    def _in_bounds(self, location):
        return all(self.upper_bound >= location) and all(self.lower_bound <= location)
    
    def _recursively_search(self, starting_node, already_found, used, swaps_used, found_words):
        next_following_characters = self.word_search.find_children(already_found)

        if not next_following_characters:
            return
        
        for direction in self.directions:
            new_node = tuple(starting_node + direction)
            if not self._in_bounds(new_node) or new_node in used:
                continue

            normal_char = self.board[new_node]

            for useful_char in next_following_characters:
                needs_swap = (normal_char != useful_char)

                if swaps_used >= 2 and needs_swap: # don't look for useful swaps if we can't swap
                    continue

                new_word = already_found + useful_char

                new_used = used + [new_node]
                new_swaps_used = swaps_used + needs_swap

                if self.word_search.find_word(new_word):
                    found_words.append((new_word, new_used, self._get_word_value(new_word), new_swaps_used))
                    self.word_search.remove(new_word)

                self._recursively_search(new_node, new_word, new_used, new_swaps_used, found_words)
    
    def find_all_words(self, available_swaps, do_multiprocessing=False):
        swaps = 2 - available_swaps
        if do_multiprocessing:
            manager = mp.Manager()
            all_found_words = manager.list()
            procs = []
        else:
            all_found_words = []
        for first in range(0, 5):
            for second in range(0, 5):
                starting_node = (first, second)
                if do_multiprocessing:
                    p = mp.Process(target=self._recursively_search, args=(starting_node, board[starting_node], [starting_node], swaps, all_found_words))
                    procs.append(p)
                    p.start()
                else:
                    self._recursively_search(starting_node, self.board[starting_node], [starting_node], swaps, all_found_words)
        if do_multiprocessing:
            for p in procs:
                p.join()
            
        return all_found_words

if __name__ == "__main__":
    frame = tk.Tk()

    frame.title("SpellCastSolver")
    frame.geometry("400x200")
    board = None

    def set_board():
        board = np.array([str(i.get("1.0", "end-1c")) for i in boxes]).reshape((5, 5))
        print(board)

    def find_solution():
        
        print(board)

    def auto_tab(event):
        event.widget.delete("1.0", "end")
        event.widget.tk_focusNext().focus()

    boxes = []
    spacing = 20
    # make a grid 5x5
    for x in range(0, 5):
        for y in range(0, 5):
            input_txt = tk.Text(frame, height=1, width=2)
            input_txt.place(x=y * spacing + 5, y=x * spacing + 5)
            input_txt.bind("<KeyPress>", auto_tab)
            boxes.append(input_txt)


    set_board = tk.Button(frame, text="set board", command=set_board)

    set_board.pack()

    zero_output_label = tk.Label(frame, text="")
    zero_output_label.pack()

    frame.mainloop()



    # board = [
    #     "flnhe", "amgta", "ovnir", "fenge", "artpw"
    # ]

    # board = np.array([list(i) for i in board])

    # solver = SpellCastSolver(board)

    # import time
    # print("finding twos")
    # s = time.time()
    
    # zeros = solver.find_all_words(0)
    # ones = solver.find_all_words(1)
    # # twos = solver.find_all_words(2, True)

    # print(time.time() - s)

    # zeros.sort(key=lambda x: x[2])
    # ones.sort(key=lambda x: x[2])

    # solution_zero = zeros[-1]
    # zero_word = solution_zero[0]
    # zero_path = solution_zero[1]

    
    # print("words")
    # with open("solutions.txt", "w+") as f:
    #     for word, path, value, swaps in [zeros[-1]]:
    #         f.write(f"zero: found '{word}' at path {path} with value {value} needing {swaps}\n")

    #     for word, path, value, swaps in [ones[-1]]:
    #         f.write(f"one: found '{word}' at path {path} with value {value} needing {swaps}\n")


    # print(twos)
    # twos.sort(key=lambda x: x[0])
    


        # for word, path, value, swaps in twos:
        #     f.write(f"two: found '{word}' at path {path} with value {value} needing {swaps}\n")

# all_found_words = solver.find_all_words(0)
# import time
# time.sleep(3)
# print("here we go"*5)



# print("finding normals")
# time.sleep(3)
# s = time.time()
# normal = solver.find_all_words(0)
# print(time.time() - s)

# print("finding ones")
# time.sleep(3)
# s = time.time()
# ones = solver.find_all_words(1)
# print(time.time() - s)



# words = open("words.txt", "r").read().split()

# print(len(solver.word_search.query('')))
# print(len(words))

# previous = 0
# for word in words:
#     previous = len(solver.word_search.query(''))
#     solver.word_search.remove(word)
#     print(previous)
#     if len(solver.word_search.query('')) - previous != -1:
#         print(word)

# # all_found_words.sort(key=lambda x: x[0])
# ones.sort(key=lambda x: x[2])

# print("words")
# for word, path, value in all_found_words:
#     print(f"found '{word}' at path {path} with value {value}")

# print("ones")
# for word, path, value in ones:
#     print(f"found '{word}' at path {path} with value {value}")

# print(solver.word_search.query("arrow"))