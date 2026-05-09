import json
import argparse
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("template_json")
parser.add_argument("output_dir")
parser.add_argument("--csv", default="./raw/pxr-challenge_structure_TEST_BLINDED.csv")
args = parser.parse_args()

with open(args.template_json) as f:
    template = json.load(f)

df = pd.read_csv(args.csv, sep=None, engine="python")
Path(args.output_dir).mkdir(exist_ok=True)

for _, row in df.iterrows():
    data = json.loads(json.dumps(template))  # copy

    data["name"] = str(row["structure"])
    data["sequences"][1]["ligand"]["smiles"] = str(row["smiles"])

    out = Path(args.output_dir) / f"{row['structure']}.json"

    with open(out, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote {out}")

print("Done.")