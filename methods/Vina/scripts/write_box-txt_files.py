import os

def parse_box_pdb(pdb_path):
    atoms = []

    with open(pdb_path, "r") as f:
        for line in f:
            if line.startswith("ATOM"):
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                atoms.append((x, y, z))

    if len(atoms) < 2:
        raise ValueError(f"Not enough atoms in {pdb_path}")

    # Last atom is the center
    center_x, center_y, center_z = atoms[-1]

    # Box corners (everything except last atom)
    xs = [a[0] for a in atoms[:-1]]
    ys = [a[1] for a in atoms[:-1]]
    zs = [a[2] for a in atoms[:-1]]

    size_x = max(xs) - min(xs)
    size_y = max(ys) - min(ys)
    size_z = max(zs) - min(zs)

    return center_x, center_y, center_z, size_x, size_y, size_z


def process_folders(root_dir="."):
    for current_dir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith("box.pdb"):
                pdb_path = os.path.join(current_dir, file)

                try:
                    center_x, center_y, center_z, size_x, size_y, size_z = parse_box_pdb(pdb_path)
                except Exception as e:
                    print(f"Skipping {pdb_path}: {e}")
                    continue

                out_name = file.replace("box.pdb", "box.txt")
                out_path = os.path.join(current_dir, out_name)

                with open(out_path, "w") as out:
                    out.write(f"center_x = {center_x:.3f}\n")
                    out.write(f"center_y = {center_y:.3f}\n")
                    out.write(f"center_z = {center_z:.3f}\n")
                    out.write(f"size_x = {size_x:.3f}\n")
                    out.write(f"size_y = {size_y:.3f}\n")
                    out.write(f"size_z = {size_z:.3f}\n")

                print(f"Wrote {out_path}")


if __name__ == "__main__":
    process_folders()
