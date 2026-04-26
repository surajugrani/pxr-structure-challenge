#!/usr/bin/env python3

import os
from schrodinger import structure
from schrodinger.structutils import build

def process_mae(mae_file):
    # Determine output filename
    base = os.path.basename(mae_file)
    out_name = base.split('_')[0] + ".pdb"

    # Read structure(s)
    reader = structure.StructureReader(mae_file)

    # If multiple structures exist, process first (adjust if needed)
    st = next(reader)

    # 1) Change residue name LIG1 -> LIG
    for res in st.residue:
        if res.pdbres.strip() == "LIG1":
            res.pdbres = "LIG"

    # 2) Remove hydrogens
    build.delete_hydrogens(st)

    # 3) Write to PDB
    with structure.StructureWriter(out_name) as writer:
        writer.append(st)

    print(f"Processed: {mae_file} -> {out_name}")


def main():
    mae_files = [f for f in os.listdir('.') if f.endswith('.cif')] ### .cif or .mae !!!

    for mae in mae_files:
        try:
            process_mae(mae)
        except Exception as e:
            print(f"Error processing {mae}: {e}")


if __name__ == "__main__":
    main()