"""
Generate complex PDB files from docked ligands and receptor.
Usage: $SCHRODINGER/run script.py <receptor.maegz> <docked.sdfgz> <output_dir>
"""

import sys
import os
from schrodinger.structure import StructureReader, StructureWriter
from schrodinger.structutils.transform import get_centroid

receptor_file = sys.argv[1]
ligand_file = sys.argv[2]
output_dir = sys.argv[3]

os.makedirs(output_dir, exist_ok=True)

# Read receptor (first structure)
receptor = next(StructureReader(receptor_file))
receptor_atom_count = receptor.atom_total

# Read all docked ligands, keep best docking score per name
best = {}
for st in StructureReader(ligand_file):
    name = st.property.get("s_m_title", "unknown")
    score = st.property.get("r_i_docking_score", float("inf"))
    if name not in best or score < best[name][1]:
        best[name] = (st, score)

# Generate complexes
for name, (lig, score) in best.items():
    complex_st = receptor.merge(lig)

    # Ligand atoms are appended after receptor atoms
    for atom in complex_st.atom:
        if atom.index > receptor_atom_count:
            atom.pdbres = "LIG "

    # Remove hydrogens
    hydrogens = [atom.index for atom in complex_st.atom if atom.element == "H"]
    complex_st.deleteAtoms(hydrogens)

    # Save
    out_path = os.path.join(output_dir, f"{name}.pdb")
    with StructureWriter(out_path) as writer:
        writer.append(complex_st)
    print(f"Wrote {out_path}")

print("Done.")