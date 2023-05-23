# SpellCast-Cheat
Cheat for the discord game SpellCast


Upon running a Tkinter window will appear.

On the left is a board representing the letters from the screen, fill this board in with the screen's letters.

On the right is a board representing the multipliers (double word, double letter, triple letter, etc.), fill these in with '2', 'd', 't', respectively.

Once both boards are filled press the "set board" button (this will save the boards into memory and initalize some data structures needed for processing)

Then press either "find no swap solution", "find one swap solution", or "find two swap solution" (which take approximately 0.5, 2, 36 seconds to run respectively) to find a solution requiring no swaps, one swaps, and two swaps.
  - Once a solution is returned the board on the left should be colored to show which letters are part of the solution, any red letters are letters required to be swapped, a text should appear saying "[number] swap solution '[solution]'", this is your solution
  
Once you're done, press "clear labels" to clear the solution information from the screen (colored boxes + "[number] swap solution..." text)
