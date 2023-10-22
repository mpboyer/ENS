from operator import *

class Node:
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
        return super().__getattribute__(name)

class ImpSufTree: 
    def __init__(self, data):
        self._string = data
        self.lastNewNode = None
        self.activeNode = None
        self.activeEdge = -1  # Position in the string at which we're counting
        self.activeLength = 0
        self.remainingSuffixCount = 0
        self.rootEnd = None
        self.splitEnd = None
        self.size = -1  # Length of input string
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
        # Rule 1, extends all leaves created so far in tree
        leafEnd = pos
        # Increment remainingSuffixCount indicating that a new suffix added to the list of suffixes yet to be added in tree
        self.remainingSuffixCount += 1
        # set lastNewNode to None while starting a new phase, indicating there is no internal node waiting for it's suffix link reset in current phase"""
        self.lastNewNode = None
        # Add all suffixes (yet to be added) one by one in tree
        while(self.remainingSuffixCount > 0):
            if (self.activeLength == 0):
                self.activeEdge = pos  # APCFALZ
            #  There is no outgoing edge starting with activeEdge from activeNode
            if (self.activeNode.children.get(self._string[self.activeEdge]) is None):
                # Rule 2 : new leaf edge
                self.activeNode.children[self._string[self.activeEdge]] = self.new_node(pos, leaf=True)
                """A new leaf edge is created in above line starting
                 from an existng node (the current activeNode), and
                 if there is any internal node waiting for it's suffix
                 link get reset, point the suffix link from that last
                 internal node to current activeNode. Then set lastNewNode
                 to None indicating no more node waiting for suffix link
                 reset."""
                if (self.lastNewNode is not None):
                    self.lastNewNode.suffixLink = self.activeNode
                    self.lastNewNode = None
            else:
                _next = self.activeNode.children.get(self._string[self.activeEdge])
                if self.walk_down(_next): 
                    continue
                # Rule 3 (current character is already on the edge)
                if (self._string[_next.start + self.activeLength] == self._string[pos]):
                    if((self.lastNewNode is not None) and (self.activeNode != self.root)):
                        self.lastNewNode.suffixLink = self.activeNode
                        self.lastNewNode = None
                    # APCFER3
                    self.activeLength += 1
                    # STOP all further processing in this phase and move on to _next phase
                    break
                    # We will be here when activePoint is in middle of the edge being traversed and current character being processed is not  on the edge (we fall off the tree). In this case, we add a new internal node and a new leaf edge going out of that new node. This is Rule 2, where a new leaf edge and a new internal node get created
                self.splitEnd = _next.start + self.activeLength - 1
                split = self.new_node(_next.start, self.splitEnd)
                self.activeNode.children[self._string[self.activeEdge]] = split
                split.children[self._string[pos]] = self.new_node(pos, leaf=True)
                _next.start += self.activeLength
                split.children[self._string[_next.start]] = _next
                if (self.lastNewNode is not None):
                    self.lastNewNode.suffixLink = split
                self.lastNewNode = split
            self.remainingSuffixCount -= 1
            if ((self.activeNode == self.root) and (self.activeLength > 0)): 
                self.activeLength -= 1
                self.activeEdge = pos - self.remainingSuffixCount + 1
            elif (self.activeNode != self.root): 
                self.activeNode = self.activeNode.suffixLink

    def build_suffix_tree(self):
        self.size = len(self._string)
        """Root is a special node with start and end indices as -1,
        as it has no parent from where an edge comes to root"""
        self.rootEnd = -1
        self.root = self.new_node(-1, self.rootEnd)
        self.activeNode = self.root  # First activeNode will be root
        for i in range(self.size):
            self.extend_suffix_tree(i)

    def walk_dfs(self, current):
        start, end = current.start, current.end
        yield self._string[start: end + 1]

        for node in current.children.values():
            if node:
                yield from self.walk_dfs(node)

    def print_dfs(self):
        for sub in self.walk_dfs(self.root):
            print(sub)

    def substrings(self):
        s = 0
        print(list(self.walk_dfs(self.root)))
        for sub in self.walk_dfs(self.root):
            print(sub)
            s += 1
        return s

def substrings(mystring):
    t = ImpSufTree(mystring)
    t.build_suffix_tree()
    return t.substrings()

print(substrings("aab"))

