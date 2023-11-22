from operator import attrgetter
import re
leafEnd = -1


class Node:
    def __init__(self, leaf):
        self.children = {}
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
        self.activeNode = self.root  
        for i in range(len(self.text)):
            self.extend_suffix_tree(i)
        return self

    def print_dfs(self):
        def string_dfs(current):
            r = self.text[current.start: current.start + self.edge_length(current)] 
            for node in current.children.values() :
                r_ = string_dfs(node)
                r_ = re.sub(f"\n", f"\n|\t", r_)
                r += f"\n" + r_
            return r
        return string_dfs(self.root)[1:]
    
    def substrings(self):
        def dfs_string(current):
            if current.end == -1 : 
                res = 0
            if not current.leaf :
                res = current.end - current.start + 1
            else :
                res = current.end - current.start + 1
            for node in current.children.values():
                res += dfs_string(node)
            return res
        return dfs_string(self.root) - 1

def substrings(text):
    return SuffixTree(text).build_suffix_tree().substrings()

def substrings_b(text):
    return len(list(set([[text[i:j+1] for i in range(len(text))] for j in range(len(text))])))

print(substrings("tatiana"))


