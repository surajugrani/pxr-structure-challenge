import os, glob, argparse
from schrodinger import structure

p = argparse.ArgumentParser()
p.add_argument("input")   # e.g. "path/to/*_pv.mae"
p.add_argument("output")  # output folder
a = p.parse_args()

os.makedirs(a.output, exist_ok=True)

for f in glob.glob(a.input):
    base = os.path.splitext(os.path.basename(f))[0].split("_")[0]
    sts = list(structure.StructureReader(f))
    receptor, ligand = sts[0], sts[1]

    # Rename ligand residue to LIG
    for atom in ligand.atom:
        atom.pdbres = "LIG "

    # Merge and delete hydrogens
    complex_st = receptor.merge(ligand)
    complex_st.deleteAtoms([atom.index for atom in complex_st.atom if atom.element == "H"])

    out = os.path.join(a.output, f"{base}.pdb")
    structure.StructureWriter(out).append(complex_st)
    print(f"Wrote {out}")