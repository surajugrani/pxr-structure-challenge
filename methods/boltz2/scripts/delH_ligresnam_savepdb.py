#!/usr/bin/env python3

import os
import sys
from schrodinger import structure
from schrodinger.structutils import build

def process_mae(mae_file, out_dir):
    # Determine output filename
    base = os.path.basename(mae_file)
    out_name = base.split('_')[0] + ".pdb"
    out_path = os.path.join(out_dir, out_name)

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
    with structure.StructureWriter(out_path) as writer:
        writer.append(st)

    print(f"Processed: {mae_file} -> {out_path}")


def main():
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    mae_files = []
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith('.cif'):  ### .cif or .mae !!!
                mae_files.append(os.path.join(root, f))

    for mae in mae_files:
        try:
            process_mae(mae, output_dir)
        except Exception as e:
            print(f"Error processing {mae}: {e}")


if __name__ == "__main__":
    main()