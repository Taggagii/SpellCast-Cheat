from utils import Trie
import numpy as np
import multiprocessing as mp
import tkinter as tk

class SpellCastSolver():
    def __init__(self, board, multiplier_board):
        self.board = np.array(board)
        self.multipler_board = multiplier_board
        

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

        self.multipliers = [] # (location, type)
        for y in range(5):
            for x in range(5):
                if self.multipler_board[y][x] != '':
                    self.multipliers.append(((y, x), self.multipler_board[y][x]))

        self.multiplier_locations = [i[0] for i in self.multipliers]

        print(self.multipliers)

        self.letter_values = np.array([1, 4, 5, 3, 1, 5, 3, 4, 1, 7, 3, 3, 4, 2, 1, 4, 8, 2, 2, 2, 4, 5, 5, 7, 4, 8])

        self.upper_bound = np.array((4, 4))
        self.lower_bound = np.array((0, 0))

    def _get_location_value(self, location):
        value = self.letter_values[ord(self.board[location]) - ord('a')]
        # todo : add a modifier here
        return value
    
    def _get_path_value(self, path, where_swaps):
        total = 0

        double_word = False

        swapped_locations, swapped_values = [i[0] for i in where_swaps], [i[1] for i in where_swaps]
        for i in path:
            letter = self.board[i]
            if i in swapped_locations:
                letter = swapped_values[swapped_locations.index(i)]

            letter_value = self.letter_values[ord(letter) - ord('a')]
            
            if i in self.multiplier_locations:
                multiplier = self.multipliers[self.multiplier_locations.index(i)][1]

                if multiplier == "d":
                    letter_value *= 2
                elif multiplier == "t":
                    letter_value *= 3
                elif multiplier == "2":
                    double_word = True

            total += letter_value

        if double_word:
            total *= 2
        return total
        # return sum([self._get_location_value(location) for location in path])
    
    def _get_word_value(self, word):
        return sum([self.letter_values[ord(i) - ord('a')] for i in word])

    def set_board(self, board):
        self.board = np.array(board)

    def _in_bounds(self, location):
        return all(self.upper_bound >= location) and all(self.lower_bound <= location)
    
    def _recursively_search(self, starting_node, already_found, used, swaps_used, where_swap, found_words):
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
                if needs_swap:
                    new_where_swap = where_swap + [(new_node, useful_char)]
                else:
                    new_where_swap = where_swap.copy()


                if self.word_search.find_word(new_word):
                    found_words.append((new_word, new_used, self._get_word_value(new_word), new_swaps_used, new_where_swap, self._get_path_value(new_used, new_where_swap)))
                    self.word_search.remove(new_word)

                self._recursively_search(new_node, new_word, new_used, new_swaps_used, new_where_swap, found_words)
    
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
                    p = mp.Process(target=self._recursively_search, args=(starting_node, board[starting_node], [starting_node], swaps, [], all_found_words))
                    procs.append(p)
                    p.start()
                else:
                    self._recursively_search(starting_node, self.board[starting_node], [starting_node], swaps, [], all_found_words)
        if do_multiprocessing:
            for p in procs:
                p.join()
            
        return all_found_words

if __name__ == "__main__":
    frame = tk.Tk()

    frame.title("SpellCastSolver")
    frame.geometry("600x200")
    solver = None
    board = None

    def cause_error(error_message):
        error_window = tk.Tk()
        error_window.geometry("200x100")
        def close():
            error_window.destroy()
        
        error_label = tk.Label(error_window, text=error_message)
        error_label.pack(pady=20)

        error_button = tk.Button(error_window, text="Ok", command=close)
        error_button.pack()

        error_window.mainloop()

    def clear_labels():
        label.config(text="")
        for i in range(5):
            for j in range(5):
                boxes[i][j].config(bg="white")

    def set_board():
        global board
        global solver
        board = np.array([[i.get("1.0", "end-1c") for i in row] for row in boxes])
        multiplier_board = np.array([[i.get("1.0", "end-1c") for i in row] for row in upgrade_boxes])
        solver = SpellCastSolver(board, multiplier_board)
        label.config(text="Board set!")

    def highlight_by_path(path, color="light blue"):
        for i in path:
            boxes[i[0]][i[1]].config(bg=color)

    def find_zero_solution():
        if not all([all(i) for i in board]):
            cause_error("Character boxes not full")
        else:
            label.config(text="Finding no swap solution")
            zero_swap_words = solver.find_all_words(0)
            # word, path, value, swapcount, where swaps used, path value
            zero_swap_words.sort(key=lambda x: x[5])
            best_zero_swap_word = zero_swap_words[-1][0]
            best_zero_swap_path = zero_swap_words[-1][1]
            highlight_by_path(best_zero_swap_path)
            print(zero_swap_words[-1])
            label.config(text=f"Zero swap solution '{best_zero_swap_word}'")

    def find_one_solution():
        if not all([all(i) for i in board]):
            cause_error("Character boxes not full")
        else:
            label.config(text="Finding one swap solution")
            zeros = solver.find_all_words(0)
            zeros.sort(key=lambda x: x[5])
            zero = zeros[-1]
            print(f"Zero word {zero}")

            one_swap_words = solver.find_all_words(1)
            # word, path, value, swapcount, where swaps used
            one_swap_words.sort(key=lambda x: x[5])
            best_one_swap_word = one_swap_words[-1][0]
            best_one_swap_path = one_swap_words[-1][1]
            best_one_swap_where = one_swap_words[-1][4]
            print(one_swap_words[-1])
            highlight_by_path(best_one_swap_path)
            highlight_by_path([i[0] for i in best_one_swap_where], "red")
            label.config(text=f"One swap solution '{best_one_swap_word}'")

    def find_two_solution():
        if not all([all(i) for i in board]):
            cause_error("Character boxes not full")
        else:
            label.config(text="Finding two swap solution")
            zeros = solver.find_all_words(0)
            ones = solver.find_all_words(1)

            zeros.sort(key=lambda x: x[5])
            ones.sort(key=lambda x: x[5])
            zero = zeros[-1]
            one = ones[-1]
            print(f"Zero word {zero}")
            print(f"One word {one}")

            two_swap_words = list(solver.find_all_words(2, True))
            # word, path, value, swapcount, where swaps used
            two_swap_words.sort(key=lambda x: x[5])
            best_two_swap_word = two_swap_words[-1][0]
            best_two_swap_path = two_swap_words[-1][1]
            best_two_swap_where = two_swap_words[-1][4]
            print(two_swap_words[-1])
            highlight_by_path(best_two_swap_path)
            highlight_by_path([i[0] for i in best_two_swap_where], "red")
            label.config(text=f"Two swap solution '{best_two_swap_word}'")

    def add_multipliers():
        label.config(text="add location of double word")


    def auto_tab(event):
        event.widget.delete("1.0", "end")
        event.widget.tk_focusNext().focus()

    boxes = []
    spacing = 20
    # make a grid 5x5
    for x in range(0, 5):
        row = []
        for y in range(0, 5):
            input_txt = tk.Text(frame, height=1, width=2)
            input_txt.place(x=y*spacing + 5, y=x*spacing + 5)
            input_txt.bind("<KeyPress>", auto_tab)
            row.append(input_txt)
        boxes.append(row)

    upgrade_boxes = []
    spacing = 20
    # make a grid 5x5
    for x in range(0, 5):
        row = []
        for y in range(0, 5):
            input_txt = tk.Text(frame, height=1, width=2)
            input_txt.place(x=495 + y*spacing, y=x*spacing + 5)
            input_txt.bind("<KeyPress>", auto_tab)
            row.append(input_txt)
        upgrade_boxes.append(row)


    set_board = tk.Button(frame, text="set board", command=set_board)
    set_board.pack()

    find_zero_solution_button = tk.Button(frame, text="find no swap solution", command=find_zero_solution)
    find_zero_solution_button.pack()

    find_one_solution_button = tk.Button(frame, text="find one swap solution", command=find_one_solution)
    find_one_solution_button.pack()

    find_two_solution_button = tk.Button(frame, text="find two swap solution", command=find_two_solution)
    find_two_solution_button.pack()

    clear_labels_button = tk.Button(frame, text="clear labels", command=clear_labels)
    clear_labels_button.pack()

    label = tk.Label(frame, text="", wraplength=200)
    label.pack()

    frame.mainloop()

