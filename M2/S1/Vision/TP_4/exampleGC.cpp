#include <iostream>

#include "maxflow/graph.h"

using namespace std;

// Use the library to compute a minimum cut on the following graph:
//
//        SOURCE
//       /       \
//     1/         \6
//     /      4    \
//   node0 -----> node1
//     |   <-----   |
//     |      3     |
//     \            /
//     5\          /1
//       \        /
//          SINK

void testGCuts() {
    Graph<int,int,int> g(2, 1); // estimated # of nodes/edges
    g.add_node(2);
    g.add_tweights( 0,   /* capacities */  1, 5 );
    g.add_tweights( 1,   /* capacities */  6, 1 );
    g.add_edge( 0, 1,    /* capacities */  4, 3 );
    int flow = g.maxflow();
    cout << "Flow = " << flow << endl;
    for (int i=0;i<2;i++)
        if (g.what_segment(i) == Graph<int,int,int>::SOURCE)
            cout << i << " is in the SOURCE set" << endl;
        else
            cout << i << " is in the SINK set" << endl;
}

int main() {
    testGCuts();
    return 0;
}
