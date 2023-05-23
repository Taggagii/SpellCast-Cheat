class TrieNode:
    """A node in the trie structure"""

    def __init__(self, char):
        # the character stored in this node
        self.char = char

        # whether this can be the end of a word
        self.is_end = False

        # a counter indicating how many times a word is inserted
        # (if this node's is_end is True)
        self.counter = 0

        # a dictionary of child nodes
        # keys are characters, values are nodes
        self.children = {}

class Trie(object):
    """The trie object"""

    def __init__(self):
        """
        The trie has at least the root node.
        The root node does not store any character
        """
        self.root = TrieNode("")
    
    def insert(self, word):
        """Insert a word into the trie"""
        node = self.root
        
        # Loop through each character in the word
        # Check if there is no child containing the character, create a new child for the current node
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                # If a character is not found,
                # create a new node in the trie
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node
        
        # Mark the end of a word
        node.is_end = True

        # Increment the counter to indicate that we see this word once more
        node.counter += 1
    
    def remove(self, word):
        node = self.root

        # assume that word is in the trie
        cur_node_char = None
        oldest_singleton = None

        for char in word:
            # print(f"character {cur_node_char} children {node.children.keys()}")
            if len(node.children) == 1 and oldest_singleton is None:
                oldest_singleton = node
            else:
                oldest_singleton = None

            cur_node_char = char
            node = node.children[char]


        if oldest_singleton is not None and not node.is_end:
            # print('we should delete node with children', oldest_singleton.children.keys())    
            oldest_singleton.children = {}
        else:
            node.is_end = False

    def find_children(self, word):
        node = self.root

        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return []
        
        return node.children.keys()
        
    def find_word(self, word):
        node = self.root
        
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return False
        
        return node.is_end

    def dfs(self, node, prefix):
        """Depth-first traversal of the trie
        
        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if node.is_end:
            self.output.append((prefix + node.char, node.counter))
        
        for child in node.children.values():
            self.dfs(child, prefix + node.char)
        
    def query(self, x):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of 
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        self.output = []
        node = self.root
        
        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return []
        
        # Traverse the trie to get all candidates
        self.dfs(node, x[:-1])

        # Sort the results in reverse order and return
        return sorted(self.output, key=lambda x: x[1], reverse=True)