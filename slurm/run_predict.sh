#!/bin/bash
#SBATCH -p gpu
#SBATCH -t 10:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4

module load cuda/11.8
#micromamba activate boltz

boltz predict ./data/processed/input_yamls_1/ --out_dir ./methods/boltz2/outputs_1
#boltz predict yamls_no-msa/ --use_msa_server --use_potentials