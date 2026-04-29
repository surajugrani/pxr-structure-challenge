#!/bin/bash

export LD_LIBRARY_PATH=$HOME:$LD_LIBRARY_PATH
echo $SCHRODINGER
$SCHRODINGER/run scripts_and_templates/prep_and_grid.py ../boltz2/2_rcy5_smpl300/_pdb_outs/ 2_Boltz2-rcy5-smpl300/