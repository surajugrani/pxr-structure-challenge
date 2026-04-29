import os, glob, argparse
from schrodinger import structure

p = argparse.ArgumentParser()
p.add_argument("input")   # e.g. "data/*.mae"
p.add_argument("output")  # output folder
a = p.parse_args()

os.makedirs(a.output, exist_ok=True)

for f in glob.glob(a.input):
    base = os.path.splitext(os.path.basename(f))[0].split("_")[0]
    for i, st in enumerate(structure.StructureReader(f)):
        st.deleteAtoms([x.index for x in st.atom if x.element == "H"])
        out = f"{base}_{i}.pdb" if i else f"{base}.pdb"
        structure.StructureWriter(os.path.join(a.output, out)).append(st)