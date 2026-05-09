#!/usr/bin/env python3

"""
Combine receptor PDB + ligand SDF into a single complex PDB.

Requirements:
- Run with Schrödinger's Python:
    $SCHRODINGER/run python make_complexes.py INPUT_DIR OUTPUT_DIR

Input structure:
INPUT_DIR/
    subfolder1/
        something_rec.pdb
        something_docked.sdf
    subfolder2/
        ...

Behavior:
- Finds exactly one *rec.pdb and one *docked.sdf per subfolder
- Reads receptor and ligand
- Renames all ligand residues to "LIG"
- Removes all hydrogens from receptor and ligand
- Merges into one structure
- Writes:
      OUTPUT_DIR/{subfoldername}.pdb
"""

import os
import sys
import glob

from schrodinger import structure


def remove_hydrogens(st):
    """
    Delete all hydrogen atoms from a structure.
    """
    delete_atoms = [atom.index for atom in st.atom if atom.atomic_number == 1]

    # deleteAtoms works in-place
    if delete_atoms:
        st.deleteAtoms(delete_atoms)


def rename_ligand_residue(st, new_resname="LIG"):
    """
    Rename all ligand residues to LIG.
    """
    for res in st.residue:
        res.pdbres = new_resname


def combine_structures(receptor, ligand):
    """
    Append ligand atoms into receptor structure.
    """
    receptor.extend(ligand)
    return receptor


def process_subfolder(subfolder, output_dir):
    """
    Process one docking folder.
    """
    subfolder_name = os.path.basename(os.path.abspath(subfolder))

    rec_files = glob.glob(os.path.join(subfolder, "*rec.pdb"))
    lig_files = glob.glob(os.path.join(subfolder, "*docked.sdf"))

    if len(rec_files) != 1:
        print(f"[SKIP] {subfolder_name}: expected 1 receptor, found {len(rec_files)}")
        return

    if len(lig_files) != 1:
        print(f"[SKIP] {subfolder_name}: expected 1 ligand, found {len(lig_files)}")
        return

    rec_file = rec_files[0]
    lig_file = lig_files[0]

    print(f"[INFO] Processing {subfolder_name}")

    # Read receptor
    receptor = next(structure.StructureReader(rec_file))

    # Read first ligand entry from SDF
    ligand = next(structure.StructureReader(lig_file))

    # Rename ligand residue
    rename_ligand_residue(ligand, "LIG")

    # Remove hydrogens
    remove_hydrogens(receptor)
    remove_hydrogens(ligand)

    # Merge
    complex_st = combine_structures(receptor, ligand)

    # Output file
    out_file = os.path.join(output_dir, f"{subfolder_name}.pdb")

    # Write PDB
    with structure.StructureWriter(out_file) as writer:
        writer.append(complex_st)

    print(f"[DONE] Wrote {out_file}")


def main():
    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "  $SCHRODINGER/run python make_complexes.py INPUT_DIR OUTPUT_DIR"
        )
        sys.exit(1)

    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])

    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory does not exist:\n{input_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    subfolders = sorted(
        [
            os.path.join(input_dir, d)
            for d in os.listdir(input_dir)
            if os.path.isdir(os.path.join(input_dir, d))
        ]
    )

    if not subfolders:
        print("No subfolders found.")
        sys.exit(1)

    for subfolder in subfolders:
        try:
            process_subfolder(subfolder, output_dir)
        except Exception as e:
            print(f"[ERROR] {subfolder}: {e}")

    print("\nAll done.")


if __name__ == "__main__":
    main()