import os
import shutil

for f in os.listdir():
    if f.endswith(".cif"):
        folder = f.split("_")[0]
        os.makedirs(folder, exist_ok=True)
        shutil.copy(f, os.path.join(folder, f))