#!/usr/bin/env python3
import json, argparse
from pathlib import Path
import pandas as pd

p = argparse.ArgumentParser()
p.add_argument("indir")
p.add_argument("out")
args = p.parse_args()

rows = []
for f in Path(args.indir).rglob("confidence*.json"):
    try:
        d = json.load(open(f))
        r = {"filename": f.name}

        for k in ["confidence_score","ptm","iptm","ligand_iptm","protein_iptm",
                  "complex_plddt","complex_iplddt","complex_pde","complex_ipde"]:
            r[k] = d.get(k)

        r.update({f"chains_ptm_{k}": v for k,v in d.get("chains_ptm",{}).items()})
        r.update({f"pair_iptm_{i}_{j}": v
                  for i,sub in d.get("pair_chains_iptm",{}).items()
                  for j,v in sub.items()})

        rows.append(r)
    except Exception as e:
        print("skip:", f, e)

pd.DataFrame(rows).to_csv(args.out, index=False)