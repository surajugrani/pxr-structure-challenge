import os
import glob
import subprocess
import time

dirs = glob.glob("*/") 
for di in dirs:
    os.chdir(di)
    print(f"\n\nCurrently working on {di}")
    p_folder=di.strip('/')
    
#    l_res = 'LIG1'
#    mae_file = [fil for fil in os.listdir('.') if fil.endswith("prepped.mae")][0]
#    print("\nNow generating grids")
#    subprocess.run(['generate_glide_grids', '-rec_file', mae_file, '-lig_asl', f'res. {l_res}', '-WAIT'])
# 
#    glide_in = f'{p_folder}_dock.in'
#    print(f"\nNow docking with {glide_in}")
#    subprocess.run(['glide', glide_in])
#    
#    glide_in1 = f'{p_folder}_min.in'
#    print(f"\nNow minimizing with {glide_in1}")
#    subprocess.run(['glide', glide_in1])
    
    glide_in_restr = f'{p_folder}_dock-restr.in'
    print(f"\nNow docking with {glide_in_restr}")
    subprocess.run(['glide', glide_in_restr])
    
    os.chdir('..')
print("Done with all folders")
time.sleep(1000)