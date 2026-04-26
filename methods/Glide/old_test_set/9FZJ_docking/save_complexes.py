#!/usr/bin/env python

from schrodinger import structure
from schrodinger.structure import StructureWriter


def remove_hydrogens(st):
    """Remove all hydrogens from a structure."""
    hydrogens = [atom.index for atom in st.atom if atom.element == "H"]
    st.deleteAtoms(hydrogens)


def prepare_ligand(lig):
    """Rename ligand residue to LIG and remove hydrogens."""
    remove_hydrogens(lig)

    for res in lig.residue:
        res.pdbres = "LIG"


def main(receptor_pdb, ligand_sdf):
    # Load receptor (assume single structure)
    receptor = next(structure.StructureReader(receptor_pdb))
    remove_hydrogens(receptor)

    # Iterate over ligands
    for lig in structure.StructureReader(ligand_sdf):
        lig_name = lig.title.strip() if lig.title else "ligand"

        # Clean ligand
        prepare_ligand(lig)

        # Create a copy of receptor to avoid modifying original
        complex_st = receptor.copy()

        # Append ligand atoms to receptor
        complex_st.extend(lig)

        # Output filename
        out_name = f"{lig_name}.pdb"

        # Write PDB
        with StructureWriter(out_name) as writer:
            writer.append(complex_st)

        print(f"Saved: {out_name}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: $SCHRODINGER/run script.py receptor.pdb ligands.sdf")
        sys.exit(1)

    receptor_pdb = sys.argv[1]
    ligand_sdf = sys.argv[2]

    main(receptor_pdb, ligand_sdf)