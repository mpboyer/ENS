"""An optimized implementation of Suffix-Tree."""

# For more infor about the comments you can read http://web.stanford.edu/~mjkay/gusfield.pdf
from operator import attrgetter
import re
leafEnd = -1


class Node:
    """The Suffix-tree's node."""

    def __init__(self, leaf):
        # self.__identifier = identifier
        self.children = {}
        # for leaf nodes, it stores the index of suffix for
        # the path  from root to leaf"""
        self.leaf = leaf
        self.suffixIndex = None
        self.start = None
        self.end = None
        self.suffixLink = None

    def __eq__(self, node):
        atg = attrgetter('start', 'end', 'suffixIndex')
        return atg(self) == atg(node)

    def __ne__(self, node):
        atg = attrgetter('start', 'end', 'suffixIndex')
        return atg(self) != atg(node)

    def __getattribute__(self, name):
        if name == 'end':
            if self.leaf:
                return leafEnd
        return super(Node, self).__getattribute__(name)


class SuffixTree:
    def __init__(self, data):
        self.text = data
        self.lastNewNode = None
        self.activeNode = None
        self.activeEdge = -1
        self.activeLength = 0
        self.remainingSuffixCount = 0
        self.root = None

    def edge_length(self, node):
        return node.end - node.start + 1

    def walk_down(self, current_node):
        length = self.edge_length(current_node)
        if (self.activeLength >= length):
            self.activeEdge += length
            self.activeLength -= length
            self.activeNode = current_node
            return True
        return False

    def new_node(self, start, end=None, leaf=False):
        node = Node(leaf)
        node.suffixLink = self.root
        node.start = start
        node.end = end
        node.suffixIndex = -1
        return node

    def extend_suffix_tree(self, pos):
        global leafEnd
        leafEnd = pos
        self.remainingSuffixCount += 1
        self.lastNewNode = None
        while(self.remainingSuffixCount > 0):
            if (self.activeLength == 0):
                self.activeEdge = pos 

            nxt = self.activeNode.children.get(self.text[self.activeEdge])
            if nxt is None:
                self.activeNode.children[self.text[self.activeEdge]] = self.new_node(pos, leaf=True)
                if (self.lastNewNode is not None):
                    self.lastNewNode.suffixLink = self.activeNode
                    self.lastNewNode = None
            
            else:
                
                if self.walk_down(nxt): 
                    continue
                
                if (self.text[nxt.start + self.activeLength] == self.text[pos]):
                    
                    if((self.lastNewNode is not None) and (self.activeNode != self.root)):
                        self.lastNewNode.suffixLink = self.activeNode
                        self.lastNewNode = None
                    
                    self.activeLength += 1
                    break
                
                split = self.new_node(nxt.start, nxt.start + self.activeLength - 1)
                self.activeNode.children[self.text[self.activeEdge]] = split
            
                split.children[self.text[pos]] = self.new_node(pos, leaf=True)
                nxt.start += self.activeLength
                split.children[self.text[nxt.start]] = nxt
                
                if (self.lastNewNode is not None):
                
                    self.lastNewNode.suffixLink = split
                self.lastNewNode = split
            self.remainingSuffixCount -= 1
            if ((self.activeNode == self.root) and (self.activeLength > 0)):
                self.activeLength -= 1
                self.activeEdge = pos - self.remainingSuffixCount + 1
            elif (self.activeNode != self.root):  
                self.activeNode = self.activeNode.suffixLink

    def walk_dfs(self, current):
        start, end = current.start, current.end
        yield self.text[start: end + 1]
        for node in current.children.values():
            if node:
                yield from self.walk_dfs(node)

    def build_suffix_tree(self):
        self.root = self.new_node(-1, -1)
        self.activeNode = self.root  # First activeNode will be root
        for i in range(len(self.text)):
            self.extend_suffix_tree(i)
        return self

    def print_dfs(self):
        def str_dfs(current):
            res = ""
            start, end = current.start, current.end
            res += self.text[start: end + 1] + "\n"
            for node in current.children.values():
                if node : 
                    res += "\t" + re.sub("\n", "\n|\t", str_dfs(node))
            return res
        print(str_dfs(self.root))
    
    def substrings(self):
        r = 0
        for sub in self.walk_dfs(self.root):
            r += len(sub)
        return r
        

def substrings(text):
    return SuffixTree(text).build_suffix_tree().substrings()
