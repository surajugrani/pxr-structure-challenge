#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ensemble docking with Glide.
Loops over receptor folders, writes a .in file for each, and runs Glide.

Usage (called by submit.sh):
    python ensemble_dock.py <docking_folder> <ligands.sdf>
"""

import os
import sys
import subprocess

def run_docking(docking_dir, ligands_sdf):
    docking_dir = os.path.realpath(docking_dir)
    ligands_sdf = os.path.realpath(ligands_sdf)

    receptors = sorted([
        d for d in os.listdir(docking_dir)
        if os.path.isdir(os.path.join(docking_dir, d))
    ])

    for receptor in receptors:
        receptor_dir = os.path.join(docking_dir, receptor)
        grid_zip     = os.path.join(receptor_dir, "generate-grids-gridgen.zip")

        if not os.path.isfile(grid_zip):
            print(f"[SKIP] {receptor} - grid zip not found")
            continue

        # Write Glide .in file
        job_name = f"{receptor}_docking_out"
        glide_in  = os.path.join(receptor_dir, f"{receptor}_dock.in")

        with open(glide_in, "w") as f:
            f.write(f"GRIDFILE   {grid_zip}\n")
            f.write(f"LIGANDFILE {ligands_sdf}\n")
            f.write(f"JOBNAME    {job_name}\n")
            f.write( "PRECISION  SP\n")
            f.write( "POSE_OUTTYPE  ligandlib\n")
            f.write( "DOCKING_METHOD  confgen\n")
            f.write( "POSTDOCK_NPOSE  1\n")

        # Run Glide
        print(f"[DOCKING] {receptor}")
        cmd = [
            f"{os.environ['SCHRODINGER']}/glide",
            "-NOJOBID",
            glide_in,
            "-OVERWRITE",
        ]
        result = subprocess.run(cmd, cwd=receptor_dir)

        if result.returncode == 0:
            print(f"[DONE]    {receptor}")
        else:
            print(f"[ERROR]   {receptor} - Glide exited with code {result.returncode}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ensemble_dock.py <docking_folder> <ligands.sdf>")
        sys.exit(1)

    run_docking(sys.argv[1], sys.argv[2])