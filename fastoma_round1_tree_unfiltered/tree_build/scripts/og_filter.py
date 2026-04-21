#!/usr/bin/env python
from tqdm.auto import tqdm
import os
import pandas as pd
import sys
tqdm.pandas()

fastoma_res_path = sys.argv[1]
te_filter_fn = sys.argv[2]
ogs_path = sys.argv[3]

# read OGs
df = pd.read_csv(os.path.join(fastoma_res_path, 'OrthologousGroups.tsv'), sep='\t')

# read TE filter
with open(te_filter_fn, 'rt') as fp:
    te_prot_ids = set(map(lambda x: x.rstrip(), fp.readlines()))

df['is_te'] = df['Protein'].progress_apply(lambda x: x in te_prot_ids)
ogs_to_filter = set(df[df['is_te']]['Group'])
no_te_ogs = set(df['Group']) - ogs_to_filter

res = ''
for fn in os.listdir(ogs_path):
    og = fn.split('.')[0]
    if og in no_te_ogs:
        if len(res) > 0:
            res += ' '
        res += os.path.join(ogs_path, fn)

print(res)
