import sys
import os
from openbabel import pybel

receptor_file = sys.argv[1]
ligand_file = sys.argv[2]
output_dir = sys.argv[3]

os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# Load receptor
# -----------------------------
receptor = next(pybel.readfile("pdb", receptor_file))
receptor.OBMol.DeleteHydrogens()   # <-- ADD THIS

# -----------------------------
# Best ligand per name
# -----------------------------
best = {}

for lig in pybel.readfile("sdf", ligand_file):

    name = lig.data["NAME"] if "NAME" in lig.data else "unknown"

    try:
        score = float(lig.data["Score"])
    except:
        score = float("inf")

    if name not in best or score < best[name][1]:
        best[name] = (lig, score)

# -----------------------------
# Write complexes SAFELY
# -----------------------------
for name, (lig, score) in best.items():

    lig.OBMol.DeleteHydrogens()   # <-- ADD THIS

    out_path = os.path.join(output_dir, f"{name}.pdb")

    with open(out_path, "w") as f:
        # receptor first
        f.write(receptor.write("pdb"))

        # ligand second (no OBMol merging!)
        f.write(lig.write("pdb"))

    print(f"Wrote {out_path}")

print("Done.")