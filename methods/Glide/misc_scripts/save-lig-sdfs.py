import os
from schrodinger import structure

for folder in os.listdir():
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.endswith(".cif"):
                cif_path = os.path.join(folder, f)
                
                # Read structure (take first structure in file)
                st = next(structure.StructureReader(cif_path))
                
                # Extract LIG1 residue
                lig_atoms = [a.index for a in st.atom if a.pdbres.strip() == "LIG1"]
                lig = st.extract(lig_atoms)
                
                # Write to SDF
                out_path = os.path.join(folder, f"{folder}.sdf")
                with structure.StructureWriter(out_path) as writer:
                    writer.append(lig)