# -*- coding: utf-8 -*-
import sys
import os

folder = sys.argv[1]

if not os.path.isdir(folder):
    raise ValueError(f"Not a valid folder: {folder}")

def rename_residue_line(line):
    # PDB residue name is columns 18–20 (0-indexed: 17:20)
    if line.startswith(("ATOM", "HETATM")):
        resname = line[17:20]
        if resname.strip() == "UNL":
            # replace with LIG, keep alignment (3 chars)
            line = line[:17] + "LIG" + line[20:]
    return line

for filename in os.listdir(folder):
    if not filename.lower().endswith(".pdb"):
        continue

    path = os.path.join(folder, filename)

    with open(path, "r") as f:
        lines = f.readlines()

    new_lines = [rename_residue_line(line) for line in lines]

    with open(path, "w") as f:
        f.writelines(new_lines)

    print(f"Updated: {filename}")

print("Done.")