#!/bin/bash
#SBATCH --partition=alphafold
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=10:00:00

module load alphafold/3.0

export TF_FORCE_UNIFIED_MEMORY=1

python $(which run_alphafold.py) \
  --input_dir=./data/processed/af3_jsons/1 \
  --output_dir=./methods/AlphaFold3/1