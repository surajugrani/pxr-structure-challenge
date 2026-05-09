#!/bin/bash
for pdb_dir in rec-lig-files/5kpy_ne*/; do # Rec-Lig_Files
    cd ${pdb_dir} || exit
    echo -e "\nCurrently processing folder $pdb_dir"
    pdb_folder=$(basename "$pdb_dir")
    #echo -e "This is ${pdb_folder}"
    pdb_name="${pdb_folder:0:4}"
    lig_file=$(ls *.sdf)
    rec_file=$(ls *rec.pdb)
    echo -e "\nPreparing receptor using mk_prepare_receptor.py with ${rec_file} and ${lig_file} ..."
    mk_prepare_receptor.py --read_pdb "${rec_file}" -o "${pdb_name}-rec" -p -j -g --allow_bad_res --box_enveloping "${lig_file}" --padding 5 --default_altloc A --add_templates ../../additional_templates.json
    echo -e "\nNow preparing grids..."    
    ../../autogrid4 -p "${pdb_name}-rec".gpf -l "${pdb_name}-rec".glg
    cd ../.. || exit
done