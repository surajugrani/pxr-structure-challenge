import os
import subprocess
from schrodinger import structure

base_dir = os.getcwd()

for folder in os.listdir(base_dir):
    if not os.path.isdir(folder):
        continue

    folder_path = os.path.join(base_dir, folder)
    os.chdir(folder_path)

    try:
        for f in os.listdir():
            if not f.endswith(".cif"):
                continue

            mae_file = f.replace(".cif", "_prepped.mae")

            print(f"Processing: {folder}/{f}")

            # Run prepwizard inside folder
            try:
                subprocess.run(
                    ["prepwizard", "-WAIT", f, mae_file],
                    check=True
                )
            except subprocess.CalledProcessError:
                print(f"Prepwizard failed for {f}")
                continue

            if not os.path.exists(mae_file):
                print(f"Missing output: {mae_file}")
                continue

            # Read structure
            st = next(structure.StructureReader(mae_file))

            # Extract LIG1
            lig_atoms = [a.index for a in st.atom if a.pdbres.strip() == "LIG1"]
            if not lig_atoms:
                print(f"No LIG1 found in {mae_file}")
                continue

            lig = st.extract(lig_atoms)

            # Write SDF named after folder
            sdf_file = f"{folder}.sdf"
            with structure.StructureWriter(sdf_file) as writer:
                writer.append(lig)

    finally:
        # Always go back to base directory
        os.chdir(base_dir)