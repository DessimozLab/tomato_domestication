#!/usr/bin/env python
from collections import Counter
from dendropy import Tree
from tqdm.auto import tqdm
import itertools
import os
import pandas as pd
import pyham
import sys


fastoma_results_path = sys.argv[1]

# load the tree and get all the branches
nwk_fn = os.path.join(fastoma_results_path, 'species_tree_checked.nwk')
t = Tree.get(path=nwk_fn, schema='newick')

n = t.seed_node
terminal_branches = []
internal_branches = []
for n1 in n.levelorder_iter():
    if n1.is_leaf():
        terminal_branches.append((n1.parent_node.label, n1.taxon.label))
    else:
        if n1.parent_node is not None:
            internal_branches.append((n1.parent_node.label, n1.label))

# orthoxml
ham = pyham.Ham(
            tree_file=nwk_fn,
            tree_format="newick",
            hog_file=os.path.join(fastoma_results_path, 'FastOMA_HOGs.orthoxml'),
            type_hog_file="orthoxml",
            filter_object=None,
            use_internal_name=True,
            with_parser_progress=True,
        )

def get_measures(ham):
    hog_qual = []
    for (hog_id, hog) in tqdm(ham.top_level_hogs.items()):
        x = hog.get_all_descendant_genes_clustered_by_species()
        n_sp_in_hog = len(x.keys())
        n_genes_in_hog = sum(1 for _ in itertools.chain.from_iterable(x.values()))
        n_sp_below_root_level = len(hog.genome.taxon.get_leaf_names())
        q = n_sp_in_hog / n_sp_below_root_level
        hog_qual.append((hog_id, q, n_genes_in_hog))

    df = pd.DataFrame(hog_qual, columns=['hog_id', 'completeness_score', 'n_members'])

    # count implied losses
    implied_losses = Counter()
    duplications_per_hog = Counter()
    stats = []
    for btype, b in tqdm(list(zip(itertools.repeat('terminal'), terminal_branches)) +
                         list(zip(itertools.repeat('internal'), internal_branches))):
        tail_genome = ham.get_ancestral_genome_by_name(b[0].replace(" ","_"))
        try:
            head_genome = ham.get_ancestral_genome_by_name(b[1].replace(" ","_"))
        except:
            head_genome = ham.get_extant_genome_by_name(b[1].replace(" ","_"))

        vmap = ham.compare_genomes_vertically(head_genome, tail_genome)
        for g in vmap.get_lost():
            fam_id = g.get_top_level_hog().hog_id
            implied_losses[fam_id] += 1

        for g in vmap.get_duplicated().keys():
            fam_id = g.get_top_level_hog().hog_id
            duplications_per_hog[fam_id] += 1

        # also want to gather the statistics about the size of each of the sets
        x = {'tail_node': b[0],
             'head_node': b[1],
             'retained_head': len(vmap.get_retained().values()),
             'retained_tail': len(vmap.get_retained().keys()),
             'gained': len(vmap.get_gained()),
             'duplicated_head': len(list(itertools.chain.from_iterable(vmap.get_duplicated().values()))),
             'duplicated_tail': len(vmap.get_duplicated().keys()),
             'lost': len(vmap.get_lost()),
             'tail_genome_size': len(tail_genome.genes),
             'head_genome_size': len(head_genome.genes),
             'branch_type': btype}
        stats.append(x)

    branch_stats = pd.DataFrame(stats)

    df['implied_losses'] = df['hog_id'].apply(lambda x: implied_losses[x])
    df['norm_losses'] = (df['implied_losses'] / df['n_members'])
    df['duplications'] = df['hog_id'].apply(lambda x: duplications_per_hog[x])
        
    return df


def get_level(hogid):
    hog = ham.get_hog_by_id(hogid)
    level = hog.get_top_level_hog().genome.name
    return level


df = get_measures(ham)
df['level'] = df.apply(lambda x: get_level(x['hog_id']), axis=1)
df.to_csv(sys.stdout, index=False, header=True, sep='\t')
