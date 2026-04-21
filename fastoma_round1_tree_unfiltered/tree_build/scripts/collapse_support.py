#!/usr/bin/env python
from dendropy import Tree
import sys

in_tree = sys.argv[1]
cutoff = float(sys.argv[2])

t = Tree.get_from_path(in_tree, schema='newick')

for e in t.internal_edges():
    if e.head_node.label is not None:
        supp = float(e.head_node.label)
        if supp < cutoff:
            e.collapse()

print(t.as_string(schema='newick'), end='')
