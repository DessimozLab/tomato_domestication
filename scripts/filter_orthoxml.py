#!/usr/bin/env python
'''
    Script to filter OrthoXML file for a set of top-level HOGs (root HOGs)
'''
from orthoxml.parsers import process_stream_orthoxml, StreamOrthoXMLParser
from orthoxml.streamfilters import filter_kwargs, NodePredicate
import sys


class HOGIDCheck(NodePredicate):
    """
    Checks if the node has at least the given number of direct children of type:
        <geneRef ...>
    """
    def __init__(self, hog_ids_to_keep):
        self.hog_ids_to_keep = hog_ids_to_keep

    def __call__(self, node):
        hog_id = node.attrib['id']
        return ((hog_id in self.hog_ids_to_keep) or
                (hog_id.split('_')[0] in self.hog_ids_to_keep))


class RemoveTopLevel(StreamOrthoXMLParser):
    """
    Based on CascadeRemoveFilter
    """
    def __init__(self, source, predicate: NodePredicate):
        super().__init__(source)
        self.predicate = predicate

    def process_toplevel_group(self, elem):
        # check if rootnode needs to be removed
        if not self.predicate(elem):
            # root element need to be removed, don't return anything
            return None
        else:
            return elem


def filter_hogs_by_id(in_fn, out_fn, hog_ids_to_keep):
    hog_filter = HOGIDCheck(hog_ids_to_keep)
    process_stream_orthoxml(in_fn,
                            out_fn,
                            parser_cls=RemoveTopLevel,
                            parser_kwargs={'predicate': hog_filter})


if __name__ == '__main__':
    args = sys.argv[1:]
    in_fn = args[0]
    filter_fn = args[1]
    out_fn = args[2]

    with open(filter_fn, 'rt') as fp:
        hogs_to_keep = set(map(lambda x: x.rstrip(), fp))

    filter_hogs_by_id(in_fn, out_fn, hogs_to_keep)
