#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process ensemble docking results.
For each ligand, picks the best scoring pose across all receptors and tautomers,
then merges it into the corresponding receptor complex (with original LIG removed).

Usage: $SCHRODINGER/run process_results.py <docking_folder> <output_dir>
"""

import sys
import os
from schrodinger.structure import StructureReader, StructureWriter


def get_receptor_name(docking_dir, receptor):
    """Return the receptor name (folder basename)."""
    return receptor


def collect_best_poses(docking_dir, receptors):
    """
    Scan all receptor docked output files and return a dict:
        { ligand_name: (score, pose_structure, receptor_name) }
    keeping only the single best scoring pose per ligand across all receptors.
    """
    best = {}  # ligand_name -> (score, structure, receptor_name)

    for receptor in receptors:
        dock_file = os.path.join(docking_dir, receptor, f"{receptor}_dock_lib.maegz")
        if not os.path.isfile(dock_file):
            print(f"[SKIP] {receptor} - docked output not found: {dock_file}")
            continue

        print(f"[READING] {receptor}")
        for st in StructureReader(dock_file):
            name  = st.property.get("s_m_title", "unknown")
            score = st.property.get("r_i_docking_score", float("inf"))

            if name not in best or score < best[name][0]:
                best[name] = (score, st, receptor)

    return best


def build_complexes(docking_dir, best, output_dir):
    """
    For each ligand in best:
      - Load the receptor complex .mae
      - Delete the existing LIG residue
      - Merge in the best docked pose, label it LIG
      - Strip hydrogens
      - Save as <ligand_name>.pdb
    """
    os.makedirs(output_dir, exist_ok=True)

    for name, (score, lig_st, receptor) in best.items():
        complex_file = os.path.join(docking_dir, receptor, f"{receptor}_complex.mae")
        if not os.path.isfile(complex_file):
            print(f"[SKIP] {name} - complex file not found: {complex_file}")
            continue

        # Load receptor complex (first structure in file)
        complex_st = next(StructureReader(complex_file))

        # Delete existing LIG residue from complex
        lig_atoms = [
            atom.index for atom in complex_st.atom
            if atom.pdbres.strip() == "LIG"
        ]
        if lig_atoms:
            complex_st.deleteAtoms(lig_atoms)
        else:
            print(f"[WARN] {name} - no LIG residue found in {complex_file}")

        receptor_atom_count = complex_st.atom_total

        # Merge best docked pose into the receptor
        complex_st = complex_st.merge(lig_st)

        # Label merged ligand atoms as LIG
        for atom in complex_st.atom:
            if atom.index > receptor_atom_count:
                atom.pdbres = "LIG "

        # Remove all hydrogens
        hydrogens = [atom.index for atom in complex_st.atom if atom.element == "H"]
        complex_st.deleteAtoms(hydrogens)

        # Write PDB
        out_path = os.path.join(output_dir, f"{name}.pdb")
        with StructureWriter(out_path) as writer:
            writer.append(complex_st)

        print(f"[WROTE] {out_path}  (score: {score:.3f}, receptor: {receptor})")

    print("Done.")


def main():
    if len(sys.argv) != 3:
        print("Usage: $SCHRODINGER/run process_results.py <docking_folder> <output_dir>")
        sys.exit(1)

    docking_dir = os.path.realpath(sys.argv[1])
    output_dir  = os.path.realpath(sys.argv[2])

    receptors = sorted([
        d for d in os.listdir(docking_dir)
        if os.path.isdir(os.path.join(docking_dir, d))
    ])

    if not receptors:
        print(f"No receptor folders found in {docking_dir}")
        sys.exit(1)

    print(f"Found {len(receptors)} receptor(s): {', '.join(receptors)}\n")

    best = collect_best_poses(docking_dir, receptors)
    print(f"\nBest poses collected for {len(best)} ligand(s). Building complexes...\n")
    build_complexes(docking_dir, best, output_dir)


if __name__ == "__main__":
    main()