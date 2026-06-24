#!/bin/bash
#SBATCH --job-name=ensemble_dock
#SBATCH --output=ensemble_dock_%j.log
#SBATCH --error=ensemble_dock_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=80:00:00
#SBATCH --partition=shared

DOCKING_DIR=$(realpath "$1")
LIGANDS_SDF=$(realpath "$2")

python ${SLURM_SUBMIT_DIR}/ensemble_dock.py "$DOCKING_DIR" "$LIGANDS_SDF"