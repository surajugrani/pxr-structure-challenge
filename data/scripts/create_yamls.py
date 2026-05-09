import pandas as pd
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("template_file")
parser.add_argument("output_dir")
args = parser.parse_args()

TEMPLATE_FILE = args.template_file
CSV_FILE = "./raw/pxr-challenge_structure_TEST_BLINDED.csv"
DUMMY_SMILES = "CCCCC"
OUTPUT_DIR = args.output_dir

with open(TEMPLATE_FILE, "r") as f:
    template = f.read()

df = pd.read_csv(CSV_FILE, sep=None, engine="python")
Path(OUTPUT_DIR).mkdir(exist_ok=True)

for _, row in df.iterrows():
    structure_name = str(row["structure"])
    smiles = str(row["smiles"])
    out = template.replace(DUMMY_SMILES, smiles)
    out_path = Path(OUTPUT_DIR) / f"{structure_name}.yaml"

    with open(out_path, "w") as f:
        f.write(out)

    print(f"Wrote {out_path}")

print("Done.")