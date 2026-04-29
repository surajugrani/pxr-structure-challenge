import os

base_dir = "./2_Boltz2-rcy5-smpl300/184folders/"  

templates = {
    "_minim.in": "./scripts_and_templates/glide_minim0.in",
    "_dock.in": "./scripts_and_templates/glide_dock0.in"
}

# Read templates once
template_contents = {
    suffix: open(path).read()
    for suffix, path in templates.items()
}

for pdb_folder in os.listdir(base_dir):
    pdb_folder_path = os.path.join(base_dir, pdb_folder)
    
    if os.path.isdir(pdb_folder_path):
        files = os.listdir(pdb_folder_path)

        ligand_file = next(
            (f for f in files if f.endswith("lig.sdf")),
            None
        )

        if ligand_file:
            for suffix, template in template_contents.items():
                modified_lines = [
                    f"LIGANDFILE   {ligand_file}" if line.strip().startswith("LIGANDFILE") else line
                    for line in template.splitlines()
                ]

                output_path = os.path.join(
                    pdb_folder_path, f"{pdb_folder}{suffix}"
                )

                with open(output_path, 'w') as out_f:
                    out_f.write("\n".join(modified_lines))

print("All Glide input files created successfully.")