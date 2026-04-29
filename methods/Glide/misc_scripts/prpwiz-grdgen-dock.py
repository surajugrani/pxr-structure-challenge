import os
import subprocess
from schrodinger import structure

for folder in os.listdir():
    if not os.path.isdir(folder):
        continue

    for f in os.listdir(folder):
        if not f.endswith(".cif"):
            continue

        cif_path = os.path.join(folder, f)
        mae_path = os.path.join(folder, f.replace(".cif", "_prepped.mae"))

        print(f"Processing: {cif_path}")

        # Run prepwizard
        try:
            subprocess.run(
                ["prepwizard", cif_path, mae_path],
                check=True
            )
        except subprocess.CalledProcessError:
            print(f"Prepwizard failed for {cif_path}")
            continue

        # Check output exists
        if not os.path.exists(mae_path):
            print(f"Missing output: {mae_path}")
            continue

        # Read structure
        st = next(structure.StructureReader(mae_path))

        # Extract LIG1
        lig_atoms = [a.index for a in st.atom if a.pdbres.strip() == "LIG1"]
        if not lig_atoms:
            print(f"No LIG1 found in {mae_path}")
            continue

        lig = st.extract(lig_atoms)

        # Write SDF
        sdf_path = os.path.join(folder, f"{folder}.sdf")
        with structure.StructureWriter(sdf_path) as writer:
            writer.append(lig)