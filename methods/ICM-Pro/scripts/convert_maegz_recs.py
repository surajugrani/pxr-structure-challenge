#!/usr/bin/env python3

import sys
from pathlib import Path
import subprocess

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <parent_folder>")
    sys.exit(1)

parent = Path(sys.argv[1]).resolve()

if not parent.is_dir():
    print(f"Error: {parent} is not a directory")
    sys.exit(1)

# Schrodinger utility
structconvert = Path(
    subprocess.check_output("which structconvert", shell=True)
    .decode()
    .strip()
)

for subdir in parent.iterdir():
    if not subdir.is_dir():
        continue

    maegz_files = list(subdir.glob("*.maegz"))

    if not maegz_files:
        print(f"[SKIP] No .maegz in {subdir.name}")
        continue

    maegz = maegz_files[0]
    out_pdb = subdir / f"{subdir.name}_rec.pdb"

    cmd = [str(structconvert), str(maegz), str(out_pdb)]

    print(f"[RUN ] {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print(f"[ OK ] Wrote {out_pdb}")
    except subprocess.CalledProcessError:
        print(f"[FAIL] {subdir.name}")