#!/usr/bin/env python
from dendropy import Tree
import sys

t = Tree.get(path=sys.argv[1], schema='newick')
print(t.as_string('newick', unquoted_underscores=True))
