#!/bin/bash
#SBATCH --job-name=vina
#SBATCH --array=1-112
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00

set -euo pipefail

rec=$(sed -n "${SLURM_ARRAY_TASK_ID}p" folder_list.txt)

cd "$rec"

pdbfol=$(basename "$rec")
pdb=${pdbfol:0:4}

rec_file=$(ls *rec*.pdbqt | head -n 1)
lig_file=$(ls *lig*.pdbqt | head -n 1)
lig=${lig_file%.pdbqt}

conf=$(ls *box.txt | head -n 1)

echo $conf

#--maps "${pdb}-rec" #--scoring vina
vina \
  --scoring vina \
  --ligand "$lig_file" \
  --receptor "$rec_file" \
  --config "$conf" \
  --out "${lig}_vina-docked.pdbqt"
