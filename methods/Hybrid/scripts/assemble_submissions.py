"""
Assemble hybrid PXR submissions by mixing structures from different sources.
Each submission has its own section below. See curation_log.md for rationale.

Usage:
    python assemble_submissions.py --submission H1
    python assemble_submissions.py --all
"""

import os
import shutil
import argparse
import zipfile
import glob
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HYBRID_DIR = os.path.join(ROOT, "methods/Hybrid")

# ── Helpers ────────────────────────────────────────────────────────────────────

def copy_structures(compound_ids, src_dir, dst_dir, label=""):
    missing = []
    for cid in compound_ids:
        src = os.path.join(src_dir, f"{cid}.pdb")
        dst = os.path.join(dst_dir, f"{cid}.pdb")
        if not os.path.exists(src):
            missing.append(cid)
            continue
        shutil.copy2(src, dst)
    if missing:
        print(f"  WARNING: {len(missing)} missing in {label}: {missing}")
    print(f"  Copied {len(compound_ids) - len(missing)} structures from {label}")
    return missing


def load_iptm(xlsx_path):
    df = pd.read_excel(xlsx_path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "compound_id", df.columns[2]: "iptm"})
    return df.set_index("compound_id")["iptm"].to_dict()


def create_zip(dst_dir, submission_name):
    zip_path = os.path.join(dst_dir, f"{submission_name}.zip")
    pdb_files = sorted(glob.glob(os.path.join(dst_dir, "*.pdb")))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for pdb in pdb_files:
            zf.write(pdb, os.path.basename(pdb))
    print(f"  Created zip: {zip_path} ({len(pdb_files)} PDBs)")


def write_manifest(dst_dir, high_ids, low_ids, overrides, high_src, low_src):
    lines = [
        f"Total structures: {len(high_ids) + len(low_ids)}",
        f"High-iPTM source ({len(high_ids)}): {high_src}",
        f"Low-iPTM source ({len(low_ids)}): {low_src}",
        f"Manual overrides routed to low-iPTM source: {sorted(overrides)}",
        "",
        "── High-iPTM compounds ──",
        "\n".join(sorted(high_ids)),
        "",
        "── Low-iPTM / override compounds ──",
        "\n".join(sorted(low_ids)),
    ]
    with open(os.path.join(dst_dir, "manifest.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# H1 — AF3+9fzj Glide-redocked (high iPTM) + Boltz2+Glide confgen (low iPTM)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H1():
    print("\n── Assembling H1 ──")

    IPTM_XLSX   = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC    = os.path.join(ROOT, "methods/Glide/5_AF3-w-9fzj-templ-iptm_redocking/docked_pdbs")
    LOW_SRC     = os.path.join(ROOT, "methods/Glide/2_Boltz2-rcy5-smpl300/docked_pdbs")
    OUT_DIR     = os.path.join(HYBRID_DIR, "H1_AF3-9fzj-glide_hiiptm_B2glide_loiptm")
    THRESHOLD   = 0.70
    OVERRIDES   = {"x01358-1"}  # known bad pose despite iPTM >= threshold

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (Glide redocked): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (Boltz2+Glide): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="Glide redocked (high iPTM)")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="Boltz2+Glide confgen (low iPTM)")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H1")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H2 — Distance-based hybrid: AF3+9fzj (dist<8Å) + Boltz2+Glide confgen (dist≥8Å)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H2():
    print("\n── Assembling H2 ──")

    AF3_DIST_CSV  = os.path.join(ROOT, "analysis/outlier_analysis/ligand_distances.csv")
    AF3_SRC       = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1")
    B2_SRC        = os.path.join(ROOT, "methods/Glide/2_Boltz2-rcy5-smpl300/docked_pdbs")
    OUT_DIR       = os.path.join(HYBRID_DIR, "H2_AF3-9fzj_dist-based_B2glide-fallback")
    THRESHOLD     = 8.0

    os.makedirs(OUT_DIR, exist_ok=True)

    af3_dist = pd.read_csv(AF3_DIST_CSV).set_index("compound_id")["distance_to_ref"].to_dict()

    af3_ids = {cid for cid, d in af3_dist.items() if pd.notna(d) and d < THRESHOLD}
    b2_ids  = {cid for cid, d in af3_dist.items() if pd.isna(d) or d >= THRESHOLD}

    print(f"  Distance threshold: {THRESHOLD} Å")
    print(f"  AF3 poses (dist < {THRESHOLD} Å): {len(af3_ids)}")
    print(f"  Boltz2+Glide fallback (dist ≥ {THRESHOLD} Å): {len(b2_ids)}")

    copy_structures(sorted(af3_ids), AF3_SRC, OUT_DIR, label="AF3+9fzj best-iPTM")
    copy_structures(sorted(b2_ids),  B2_SRC,  OUT_DIR, label="Boltz2+Glide confgen")

    # Manifest
    lines = [
        f"Selection criterion: AF3 ligand distance from 9fzj binding site",
        f"Distance threshold: {THRESHOLD} Å",
        f"Total structures: {len(af3_ids) + len(b2_ids)}",
        f"AF3+9fzj source ({len(af3_ids)}): {AF3_SRC}",
        f"Boltz2+Glide fallback ({len(b2_ids)}): {B2_SRC}",
        "",
        "── AF3 compounds (dist < 8 Å) ──",
        "\n".join(sorted(af3_ids)),
        "",
        "── Boltz2+Glide compounds (dist ≥ 8 Å) ──",
        "\n".join(sorted(b2_ids)),
    ]
    with open(os.path.join(OUT_DIR, "manifest.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")

    create_zip(OUT_DIR, "H2")
    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H3 — AF3+9fzj PrepWiz-prepared (high iPTM) + Boltz2+Glide confgen (low iPTM)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H3():
    print("\n── Assembling H3 ──")

    IPTM_XLSX = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC  = os.path.join(ROOT, "methods/Glide/5_AF3-w-9fzj-templ-iptm_redocking/prepwizzed")
    LOW_SRC   = os.path.join(ROOT, "methods/Glide/2_Boltz2-rcy5-smpl300/docked_pdbs")
    OUT_DIR   = os.path.join(HYBRID_DIR, "H3_AF3-9fzj-prepwiz_hiiptm_B2glide_loiptm")
    THRESHOLD = 0.70
    OVERRIDES = {"x01358-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (AF3+9fzj PrepWiz): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (Boltz2+Glide confgen): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="AF3+9fzj PrepWiz")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="Boltz2+Glide confgen")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H3")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H4 — AF3+9fzj mininplace-minimized (high iPTM) + Boltz2+Glide confgen (low iPTM)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H4():
    print("\n── Assembling H4 ──")

    IPTM_XLSX = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC  = os.path.join(ROOT, "methods/Glide/5_AF3-w-9fzj-templ-iptm_redocking/minimized_pdbs")
    LOW_SRC   = os.path.join(ROOT, "methods/Glide/2_Boltz2-rcy5-smpl300/docked_pdbs")
    OUT_DIR   = os.path.join(HYBRID_DIR, "H4_AF3-9fzj-mininplace_hiiptm_B2glide_loiptm")
    THRESHOLD = 0.70
    OVERRIDES = {"x01358-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (AF3+9fzj mininplace): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (Boltz2+Glide confgen): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="AF3+9fzj mininplace")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="Boltz2+Glide confgen")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H4")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H5 — AF3+9fzj best-iPTM (high iPTM) + ICM-Pro Boltz2 docked (low iPTM)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H5():
    print("\n── Assembling H5 ──")

    IPTM_XLSX = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC  = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1")
    LOW_SRC   = os.path.join(ROOT, "methods/ICM-Pro/2_Boltz2-rcy5-smpl300/docked_pdb_outs")
    OUT_DIR   = os.path.join(HYBRID_DIR, "H5_AF3-9fzj_hiiptm_B2icm_loiptm")
    THRESHOLD = 0.70
    OVERRIDES = {"x01358-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (AF3+9fzj best-iPTM): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (ICM-Pro Boltz2 docked): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="AF3+9fzj best-iPTM")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="ICM-Pro Boltz2 docked")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H5")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# Add new submissions below following the same pattern
# ══════════════════════════════════════════════════════════════════════════════


# ── Entry point ────────────────────────────────────────────────────────────────

SUBMISSIONS = {"H1": assemble_H1, "H2": assemble_H2, "H3": assemble_H3, "H4": assemble_H4, "H5": assemble_H5}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--submission", choices=SUBMISSIONS.keys(), help="Assemble a specific submission")
    group.add_argument("--all", action="store_true", help="Assemble all submissions")
    args = parser.parse_args()

    if args.all:
        for fn in SUBMISSIONS.values():
            fn()
    else:
        SUBMISSIONS[args.submission]()

    print("\nDone.")
