import pandas as pd
from pathlib import Path
import copy
import yaml

# -----------------------------
# CONFIG
# -----------------------------
TEMPLATE_FILE = "../raw/template.yaml"
CSV_FILE = "../raw/pxr-challenge_structure_TEST_BLINDED.csv"
OUTPUT_DIR = "input_yamls_1"

# -----------------------------
# LOAD TEMPLATE
# -----------------------------
with open(TEMPLATE_FILE, "r") as f:
    template = yaml.safe_load(f)

# -----------------------------
# LOAD CSV
# -----------------------------
df = pd.read_csv(CSV_FILE, sep=None, engine="python")  # auto-detect delimiter

# -----------------------------
# CREATE OUTPUT DIR
# -----------------------------
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# -----------------------------
# GENERATE YAML FILES
# -----------------------------
for _, row in df.iterrows():
    structure_name = str(row["structure"])
    smiles = str(row["smiles"])

    # deep copy template so we don't mutate original
    yaml_data = copy.deepcopy(template)

    # update SMILES (ligand is always second entry in your template)
    yaml_data["sequences"][1]["ligand"]["smiles"] = smiles

    # output path
    out_path = Path(OUTPUT_DIR) / f"{structure_name}.yaml"

    # write YAML
    with open(out_path, "w") as f:
        yaml.dump(yaml_data, f, sort_keys=False)

    print(f"Wrote {out_path}")

print("Done.")