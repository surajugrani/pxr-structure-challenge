#!/bin/bash
#SBATCH -p gpu
#SBATCH -t 10:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4

module load cuda/11.8
#micromamba activate boltz

boltz predict ./data/processed/input_yamls_w-PDBtempl_colabfoldmsa --out_dir ./methods/boltz2/3PDBtempl-colfolmsa --recycling_steps 5 --sampling_steps 300
#boltz predict ./data/processed/input_yamls_colabfold_msa --out_dir ./methods/boltz2/rcy6_smpl400 --recycling_steps 6 --sampling_steps 400
#boltz predict yamls_no-msa/ --use_msa_server --use_potentials
