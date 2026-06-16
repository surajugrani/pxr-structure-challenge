"""
Prepare Boltz predicted complexes for Glide docking.
For each complex .pdb: creates folder, runs prepwizard, extracts ligand as .sdf, runs grid generation.
Usage: $SCHRODINGER/run prep_and_grid.py <pdb_folder> <output_folder>
"""

import sys
import os
import subprocess
from schrodinger.structure import StructureReader, StructureWriter

pdb_folder = sys.argv[1]
output_folder = sys.argv[2]

os.makedirs(output_folder, exist_ok=True)

pdb_files = [f for f in os.listdir(pdb_folder) if f.endswith(".pdb")]

for pdb_file in pdb_files:
    name = os.path.splitext(pdb_file)[0]
    pdb_path = os.path.abspath(os.path.join(pdb_folder, pdb_file))
    work_dir = os.path.join(output_folder, name)
    os.makedirs(work_dir, exist_ok=True)

    complex_mae = os.path.abspath(os.path.join(work_dir, f"{name}_complex.mae"))
    lig_sdf = os.path.join(work_dir, f"{name}_lig.sdf")

    print(f"\nProcessing {name}...")

    # Step 1: Run prepwizard on complex
    subprocess.run([
        "prepwizard", "-NOJOBID", pdb_path, complex_mae
    ], cwd=work_dir, check=True)

    # Step 2: Extract LIG residue as .sdf
    for st in StructureReader(complex_mae):
        lig_atoms = [a.index for a in st.atom if a.pdbres.strip() == "LIG"]
        if lig_atoms:
            lig_st = st.extract(lig_atoms)
            with StructureWriter(lig_sdf) as w:
                w.append(lig_st)
        break  # only first structure

    # Step 3: Run grid generation centered on LIG
    subprocess.run([
        "generate_glide_grids", "-NOJOBID",
        "-rec_file", complex_mae,
        "-lig_asl", "res. LIG"
    ], cwd=work_dir, check=True)

    print(f"Done: {name}")

print("\nAll complexes processed.")