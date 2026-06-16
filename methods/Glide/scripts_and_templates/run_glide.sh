#!/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G

export LD_LIBRARY_PATH=$HOME:$LD_LIBRARY_PATH
echo $SCHRODINGER
$SCHRODINGER/run scripts_and_templates/run-glide-2.py