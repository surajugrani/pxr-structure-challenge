#!/usr/bin/env python3

import os
import sys
from schrodinger import structure


def cif_to_pdb(cif_file, out_dir):
    # Output filename: cif_filename.split('_')[0] + '.pdb'
    base = os.path.basename(cif_file)
    pdb_name = base.split('_')[0] + ".pdb"
    out_path = os.path.join(out_dir, pdb_name)

    # Read structure
    st = next(structure.StructureReader(cif_file))

    # Rename all non-protein residues to LIG
    for res in st.residue:
        if not res.isStandardResidue():
            res.pdbres = "LIG"

    # Write PDB
    with structure.StructureWriter(out_path) as writer:
        writer.append(st)

    print(f"Wrote: {out_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: run script.py folder/*/*.cif pdb-out-dir")
        sys.exit(1)

    out_dir = sys.argv[-1]
    cif_files = sys.argv[1:-1]

    os.makedirs(out_dir, exist_ok=True)

    for cif_file in cif_files:
        try:
            cif_to_pdb(cif_file, out_dir)
        except Exception as e:
            print(f"Failed: {cif_file} -> {e}")


if __name__ == "__main__":
    main()