#!/usr/bin/env python3
import os
import sys
import json
import glob
from schrodinger import structure
import openpyxl

def get_best_cif(complex_dir):
    best_iptm = -1.0
    best_ranking_score = None
    best_cif = None
    for summary_json in glob.glob(
        os.path.join(complex_dir, "seed-*", "*_summary_confidences.json")
    ):
        try:
            with open(summary_json) as f:
                data = json.load(f)
            iptm = data["iptm"]
            if iptm > best_iptm:
                best_iptm = iptm
                best_ranking_score = data.get("ranking_score")
                best_cif = summary_json.replace(
                    "_summary_confidences.json", "_model.cif"
                )
        except Exception as e:
            print(f"Warning: failed to read {summary_json}: {e}")
    if best_cif is None:
        raise RuntimeError(f"No sample predictions found in {complex_dir}")
    print(f"Selected {best_cif} (iptm={best_iptm:.3f})")
    return best_cif, best_ranking_score, best_iptm

def cif_to_pdb(cif_file, out_dir):
    base = os.path.basename(cif_file)
    pdb_name = base.split('_')[0] + ".pdb"
    out_path = os.path.join(out_dir, pdb_name)
    st = next(structure.StructureReader(cif_file))
    for res in st.residue:
        if not res.isStandardResidue():
            res.pdbres = "LIG"
    with structure.StructureWriter(out_path) as writer:
        writer.append(st)
    print(f"Wrote: {out_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: run script.py folder pdb-out-dir")
        sys.exit(1)
    folder, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    complex_dirs = [
        d for d in glob.glob(os.path.join(folder, "*"))
        if os.path.isdir(d)
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Folder Name", "Ranking Score", "iPTM"])

    for complex_dir in complex_dirs:
        try:
            best_cif, ranking_score, iptm = get_best_cif(complex_dir)
            cif_to_pdb(best_cif, out_dir)
            ws.append([os.path.basename(complex_dir), ranking_score, iptm])
        except Exception as e:
            print(f"Failed: {complex_dir} -> {e}")

    wb.save(os.path.join(out_dir, "results.xlsx"))

if __name__ == "__main__":
    main()