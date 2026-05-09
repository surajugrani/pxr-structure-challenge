#!/bin/bash
#for pdb in No-Cofac/*/; do
for pdb in 184folders/*/; do

    echo -e "\nCurrently processing ligand for $pdb"
    cd "$pdb"
    lig_file=$(ls *lig*.sdf) # *rec*.pdb
    lig=${lig_file%%.sdf}
    echo -e "Ligand file: ${lig_file}"
    obabel $lig_file -O "${lig}_V2000.sdf" # mol2
    echo -e "Converted to sdf..."
    cd ../..
done