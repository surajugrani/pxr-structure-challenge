#!/bin/bash
#SBATCH --partition=alphafold
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=20:00:00

module load alphafold/3.0

export TF_FORCE_UNIFIED_MEMORY=1

python $(which run_alphafold.py) \
  --input_dir=./data/processed/af3_jsons/5_9fzj-templ_multiseed/ \
  --output_dir=./methods/AlphaFold3/5_9fzj-templ_multiseed/