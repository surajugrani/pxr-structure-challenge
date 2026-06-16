#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

export LD_LIBRARY_PATH=$HOME:$LD_LIBRARY_PATH
echo $SCHRODINGER
$SCHRODINGER/run scripts/prep_and_grid.py Docking_14-recs/14complexes/ Docking_14-recs/Docking