#!/bin/bash
for pdb in rec-lig-files/*/; do
    echo -e "\nCurrently processing ligand for $pdb"
    cd "$pdb"
    lig_file=$(ls *.sdf)
    lig=${lig_file%%.sdf}
    echo -e "Ligand file: ${lig_file}"
    obabel $lig_file -O "${lig}.pdbqt" --partialcharge gasteiger
    echo -e "Converted to pdbqt..."
    #obabel $lig_file -O "${lig}_mmff94.pdbqt" --partialcharge mmff94
    cd ../..
done