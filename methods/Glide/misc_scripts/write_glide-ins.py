import os

# Read template glide_minim0.in
with open('glide_restr-dock0.in', 'r') as f:
    template = f.read()

# Traverse each PDB folder
for pdb_folder in os.listdir():
    if os.path.isdir(pdb_folder):
        pdb_id = pdb_folder
        ligand_file = None

        # Look for ligand file: contains 'x' and ends with '.sdf'
        for file in os.listdir(pdb_folder):
            if "x" in file and file.endswith("1.sdf"):
                ligand_file = file
                break
        
        # Proceed only if a ligand file is found
        if ligand_file:
            # Modify the template
            modified_lines = []
            for line in template.splitlines():
                if line.strip().startswith("LIGANDFILE"):
                    modified_lines.append(f"LIGANDFILE   {ligand_file}")
                elif line.strip().startswith("REF_LIGAND_FILE"):
                    modified_lines.append(f"REF_LIGAND_FILE   {ligand_file}")
                else:
                    modified_lines.append(line)
            
            modified_content = "\n".join(modified_lines)

            # Save file as PDBID-CONF_glide_minim.in
            output_filename = f"{pdb_folder}_dock-restr.in"
            output_path = os.path.join(pdb_folder, output_filename)
            with open(output_path, 'w') as out_f:
                out_f.write(modified_content)

print("Glide docking input files created successfully.")