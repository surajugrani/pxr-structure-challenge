import pandas as pd
from pathlib import Path

TEMPLATE_FILE = "../raw/template.yaml"
CSV_FILE = "../raw/pxr-challenge_structure_TEST_BLINDED.csv"
DUMMY_SMILES = "CCCCC"
OUTPUT_DIR = "input_yamls_colabfold_msa"

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