#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

export LD_LIBRARY_PATH=$HOME:$LD_LIBRARY_PATH
echo $SCHRODINGER
$SCHRODINGER/run scripts_and_templates/prep_and_grid.py 5_AF3-w-9fzj-templ-iptm_redocking/job-failed_or_manual-fix/ 5_AF3-w-9fzj-templ-iptm_redocking/job-failed_or_manual-fix/