#!/usr/bin/env python3

import os
import sys
from schrodinger import structure
from schrodinger.structutils import analyze

def remove_lig_and_save_pdb(root_dir):
    """
    Traverse each subfolder in root_dir, find files ending with '_complex.mae',
    remove residues named 'LIG', and save as PDB with filename ending in 'rec.pdb'.
    """

    for subdir, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith("_complex.mae"):

                mae_path = os.path.join(subdir, fname)

                # Output filename:
                # example: protein_complex.mae -> protein_rec.pdb
                out_name = fname.replace("complex.mae", "rec.pdb")
                out_path = os.path.join(subdir, out_name)

                print(f"Processing: {mae_path}")

                # Read first structure from MAE
                st = next(structure.StructureReader(mae_path))

                # Find residues named LIG
                lig_residues = [
                    res for res in st.residue
                    if res.pdbres.strip() == "LIG"
                ]

                # Collect atom indices to delete
                atoms_to_delete = []
                for res in lig_residues:
                    atoms_to_delete.extend([atom.index for atom in res.atom])

                # Delete atoms if any LIG residues found
                if atoms_to_delete:
                    st.deleteAtoms(atoms_to_delete)
                    print(f"  Removed {len(lig_residues)} LIG residue(s)")
                else:
                    print("  No LIG residues found")

                # Write receptor-only PDB
                with structure.StructureWriter(out_path) as writer:
                    writer.append(st)

                print(f"  Saved: {out_path}\n")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <root_directory>")
        sys.exit(1)

    root_dir = sys.argv[1]

    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a valid directory")
        sys.exit(1)

    remove_lig_and_save_pdb(root_dir)


if __name__ == "__main__":
    main()