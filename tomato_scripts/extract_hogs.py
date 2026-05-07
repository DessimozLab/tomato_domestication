#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 14:16:16 2026
Using zoo function (Adrian)
@author: ijulcach
"""

import argparse
from typing import Set, Optional
import lxml.etree as etree
import logging
from .orthoxml_parser import StreamOrthoXMLParser, OrthoXMLStreamWriter, process_stream_orthoxml


logger = logging.getLogger(__name__)

class FilterHOGSubsetWithContainedGenes(StreamOrthoXMLParser):
    """Filter based on gene_ids and roothog_ids.

    This StreamOrthoXMLParser filters an input orthoxml and returns a filtered
    instance of the species elements with only the genes listed in the gene_ids.
    It further returns only toplevel ortholog group that either contain at least
    one of the gene_ids or the toplevel hog id matches one of the roothog_ids.

    :param source: input orthoxml file
    :param roothog_ids: set of roothog_ids to filter on
    :param gene_ids: set of internal gene ids to filter on
                     (e.g. the <gene id='xxx'> attribute)
    """
    def __init__(self, source, roothog_ids=None, gene_ids=None):
        super().__init__(source)
        self.gene_ids = gene_ids or set()
        self.roothog_ids = roothog_ids or set()

    def process_species(self, elem):
        for child in elem.iter(f"{{{self._ns}}}gene"):
            if child.get('id') not in self.gene_ids:
                child.getparent().remove(child)
        return elem

    def process_toplevel_group(self, elem):
        if elem.get('id') in self.roothog_ids:
            return elem
        for gene in elem.iter(f"{{{self._ns}}}geneRef"):
            if gene.get('id') in self.gene_ids:
                return elem
        return None

def get_hog_list(inFile):
    hogs = set()
    for line in open(inFile):
        line = line.strip()
        hogs.add(line)
    print(f'Number of hogs to keep {len(hogs)}')
    return hogs

def find_gene_refs_in_selection(orthoxml, roothog_ids:Optional[Set[str]] = None):
    logger.info("start mapping of orthoxml formatted input file")
    roothog_ids = roothog_ids or set()

    genes = set()
    if len(roothog_ids) == 0:
        # nothing to do
        return genes

    nsmap = {}
    og_level = 0
    og_matches = False
    gene_refs = set()


    def fixtag(tag, ns=""):
        return "{" + nsmap[ns] + "}" + tag

    for event, elem in etree.iterparse(orthoxml, events=('start-ns', 'start', 'end')):
        if event == 'start-ns':
            ns, url = elem
            nsmap[ns] = url
        elif event == 'start' and elem.tag == fixtag('orthologGroup'):
            og_level += 1
        elif event == 'start' and elem.tag == fixtag('geneRef'):
            if elem.get('id') in gene_refs:
                og_matches = True
        elif event == 'end':
            if elem.tag == fixtag('orthologGroup'):
                og_level -= 1
                if og_level == 0:
                    if elem.get('id') in roothog_ids or og_matches:
                        # collect all genes in this group
                        genes.update(child.get('id') for child in elem.iter(fixtag('geneRef')))
                    elem.clear()
                    og_matches = False
    return genes


def extract_subset_from_orthoxml(source_orthoxml, out, roothog_ids:Optional[Set[str]] = None):
    """
    Filter an OrthoXML file to include only specific orthologGroups and their associated genes.

    This function filters an input orthoXML file to only contain the groups specified by the two filter input variables,
    roothog_ids and prot_ids. The function uses an XML writer to create a new file with the filtered content.

    The roothog_ids parameter is a set of orthologGroup IDs that should be included in the output file.
    Note that these orthologGroup IDs are expected to be at the top level of the XML hierarchy, i.e. the
    function does not work for sub-HOGs.

    The prot_ids parameter is a set of protein IDs that should be included in the output file. All rootHOGs which contain
    at least one gene from this set will be included in the output file.

    The parameters roothog_ids and prot_ids are optional, but can be combined. If both are provided, the function will
    include the union of the roothog sets that are matched by the prot_ids and the roothog_ids.

    Example:

    >>> extract_subset_from_orthoxml("input.orthoxml", "output.orthoxml", roothog_ids={"OG1", "OG2"}, prot_ids={"P1", "P2"})

    :param source_orthoxml: input orthoxml file
    :param out: output file name
    :param roothog_ids: set of orthologGroup IDs to include in the output file
    :type roothog_ids: Set[str] or None
    :param prot_ids: set of protein IDs defining ortholog groups to include in the output file.
                     are read from the gene's protId attribute.
    :type prot_ids: Set[str] or None
    """
    roothog_ids = roothog_ids or set()
    genes = find_gene_refs_in_selection(source_orthoxml, roothog_ids=roothog_ids)

    process_stream_orthoxml(source_orthoxml,
                            out,
                            parser_cls=FilterHOGSubsetWithContainedGenes,
                            parser_kwargs={'roothog_ids': roothog_ids, 'gene_ids': genes})


def main():
    # Parser for shared options between commands
    shared_args_parser = argparse.ArgumentParser(add_help=False)
    shared_args_parser.add_argument(
        "--log",
        default="WARNING",
        help="Set the logging level [DEBUG | INFO | WARNING | ERROR | CRITICAL]",
    )

    parser = argparse.ArgumentParser(
        description="Extract hogs from an orthoxml file",
    )
    parser.add_argument("-i", "--infile", dest='infile',
                        required=True,
                        help="orthoxml file"
    )
    parser.add_argument("-o", "--outfile", dest='outfile',
                        required=True,
                        help="outfile name"
    )
    parser.add_argument("-t", "--hogs", dest='hogs',
                        required=True,
                        help="list of hogs to be kept"
    )
    args = parser.parse_args()
    
    extract_subset_from_orthoxml(args.infile, args.outfile, get_hog_list(args.hogs))
    
    

if __name__ == "__main__":
    main()
