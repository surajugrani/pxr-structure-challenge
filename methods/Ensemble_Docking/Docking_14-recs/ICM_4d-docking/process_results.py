#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Process ICM 4D docking results.

For each ligand NAME:
    - Find the lowest-scoring entry in the SDF
    - Determine the receptor from RecConf
    - Load the corresponding receptor PDB
    - Remove existing LIG residue
    - Merge docked ligand
    - Rename merged ligand atoms to LIG
    - Remove hydrogens
    - Write <NAME>.pdb

Usage:
    $SCHRODINGER/run process_icm_results.py \
        results.sdf \
        recconf_map.txt \
        receptor_pdb_folder \
        output_dir
"""

import csv
import os
import sys

from schrodinger.structure import StructureReader, StructureWriter


def read_receptor_map(map_file):
    """
    Reads:
        1   8r82
        2   1skx
        ...

    Returns:
        {1: "8r82", 2: "1skx", ...}
    """
    mapping = {}

    with open(map_file, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()

            if not line:
                continue

            fields = line.split()

            recconf = int(fields[0])
            receptor = fields[1]

            mapping[recconf] = receptor

    return mapping


def collect_best_poses(sdf_file):
    """
    Returns:

        {
            ligand_name:
                (score, structure, recconf)
        }

    keeping only the lowest-scoring entry for each ligand.
    """
    best = {}

    for st in StructureReader(sdf_file):


        name = st.property["s_sd_NAME"]
        score = float(st.property["r_sd_Score"])
        recconf = int(st.property["i_sd_RecConf"])

        if name not in best or score < best[name][0]:
            best[name] = (score, st, recconf)

    return best


def build_complexes(best, receptor_map, receptor_dir, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    summary_file = os.path.join(output_dir, "summary.csv")

    with open(summary_file, "w", newline="") as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(
            ["ligand", "score", "recconf", "receptor"]
        )

        for name, (score, lig_st, recconf) in best.items():

            if recconf not in receptor_map:
                print(
                    f"[SKIP] {name} - RecConf {recconf} "
                    f"not found in mapping file"
                )
                continue

            receptor = receptor_map[recconf]

            receptor_file = os.path.join(
                receptor_dir,
                f"{receptor}.pdb"
            )

            if not os.path.isfile(receptor_file):
                print(
                    f"[SKIP] {name} - receptor file not found: "
                    f"{receptor_file}"
                )
                continue

            receptor_st = next(StructureReader(receptor_file))

            #lig_atoms = [
            #    atom.index
            #    for atom in receptor_st.atom
            #    if atom.pdbres.strip() == "LIG"
            #]

            #if lig_atoms:
            #    receptor_st.deleteAtoms(lig_atoms)

            receptor_atom_count = receptor_st.atom_total

            complex_st = receptor_st.merge(lig_st)

            for atom in complex_st.atom:
                if atom.index > receptor_atom_count:
                    atom.pdbres = "LIG "

            hydrogens = [
                atom.index
                for atom in complex_st.atom
                if atom.element == "H"
            ]

            if hydrogens:
                complex_st.deleteAtoms(hydrogens)

            out_file = os.path.join(
                output_dir,
                f"{name}.pdb"
            )

            with StructureWriter(out_file) as writer_pdb:
                writer_pdb.append(complex_st)

            writer.writerow(
                [name, score, recconf, receptor]
            )

            print(
                f"[WROTE] {out_file} "
                f"(score={score:.3f}, receptor={receptor})"
            )

    print(f"\nSummary written to {summary_file}")
    print("Done.")


def main():

    if len(sys.argv) != 5:
        print(
            "Usage:\n"
            "$SCHRODINGER/run process_icm_results.py "
            "<results.sdf> "
            "<recconf_map.txt> "
            "<receptor_pdb_folder> "
            "<output_dir>"
        )
        sys.exit(1)

    sdf_file = os.path.realpath(sys.argv[1])
    map_file = os.path.realpath(sys.argv[2])
    receptor_dir = os.path.realpath(sys.argv[3])
    output_dir = os.path.realpath(sys.argv[4])

    receptor_map = read_receptor_map(map_file)

    best = collect_best_poses(sdf_file)

    print(
        f"Found best poses for "
        f"{len(best)} ligand(s)."
    )

    build_complexes(
        best,
        receptor_map,
        receptor_dir,
        output_dir
    )


if __name__ == "__main__":
    main()