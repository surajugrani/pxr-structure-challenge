import os
import glob
import subprocess

base_dir = os.getcwd()

dirs = glob.glob("./5_AF3-w-9fzj-templ-iptm_redocking/184_folders/*/") 

for di in dirs:
    os.chdir(di)
    print(f"\n\nCurrently working on {di}")

    p_folder = os.path.basename(os.path.normpath(di))

    files = os.listdir('.')

    if not any(f.endswith('minim_lib.sdf') for f in files): # not applicable here 
        glide_in2 = f'{p_folder}_minim.in'
        print(f"\nNow running mininplace with {glide_in2}")
        subprocess.run(['glide', '-NOJOBID', glide_in2])

    if not any(f.endswith('dock_lib.sdf') for f in files): # not applicable here
        glide_in3 = f'{p_folder}_dock.in'
        print(f"\nNow running confgen with {glide_in3}")
        subprocess.run(['glide', '-NOJOBID', glide_in3])

    os.chdir(base_dir)

print("Done with all folders")