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
# H6 — AF3+9fzj best-iPTM + Boltz2+Glide confgen fallback (MW<250 OR iPTM<0.70 OR outlier)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H6():
    print("\n── Assembling H6 ──")

    from rdkit import Chem
    from rdkit.Chem import Descriptors

    SMILES_CSV  = os.path.join(ROOT, "data/raw/pxr-challenge_structure_TEST_BLINDED.csv")
    IPTM_XLSX   = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC    = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1")
    LOW_SRC     = os.path.join(ROOT, "methods/Glide/2_Boltz2-rcy5-smpl300/docked_pdbs")
    OUT_DIR     = os.path.join(HYBRID_DIR, "H6_AF3-9fzj_mw-iptm-outlier_B2glide-fallback")
    MW_THRESHOLD   = 250.0
    IPTM_THRESHOLD = 0.70
    OVERRIDES      = {"x01358-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    # Compute MW from SMILES
    smi_df = pd.read_csv(SMILES_CSV)
    smi_df.columns = smi_df.columns.str.strip()
    mw = {}
    for _, row in smi_df.iterrows():
        mol = Chem.MolFromSmiles(row["smiles"])
        mw[row["structure"]] = Descriptors.MolWt(mol) if mol else None

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    fallback_ids = {
        cid for cid in all_ids
        if (mw.get(cid) is not None and mw[cid] < MW_THRESHOLD)
        or iptm.get(cid, 1.0) < IPTM_THRESHOLD
        or cid in OVERRIDES
    }
    af3_ids = all_ids - fallback_ids

    low_mw   = {cid for cid in all_ids if mw.get(cid) is not None and mw[cid] < MW_THRESHOLD}
    low_iptm = {cid for cid in all_ids if iptm.get(cid, 1.0) < IPTM_THRESHOLD}

    print(f"  MW threshold: {MW_THRESHOLD} Da  →  {len(low_mw)} compounds")
    print(f"  iPTM threshold: {IPTM_THRESHOLD}  →  {len(low_iptm)} compounds")
    print(f"  Manual overrides: {sorted(OVERRIDES)}")
    print(f"  Total fallback (union): {len(fallback_ids)}")
    print(f"  AF3 (kept): {len(af3_ids)}")

    copy_structures(sorted(af3_ids),      HIGH_SRC, OUT_DIR, label="AF3+9fzj best-iPTM")
    copy_structures(sorted(fallback_ids), LOW_SRC,  OUT_DIR, label="Boltz2+Glide confgen")

    lines = [
        f"Fallback criteria: MW < {MW_THRESHOLD} Da OR iPTM < {IPTM_THRESHOLD} OR manual override",
        f"Total structures: {len(af3_ids) + len(fallback_ids)}",
        f"AF3+9fzj source ({len(af3_ids)}): {HIGH_SRC}",
        f"Boltz2+Glide fallback ({len(fallback_ids)}): {LOW_SRC}",
        f"  - Low MW only (not low iPTM): {sorted(low_mw - low_iptm - OVERRIDES)}",
        f"  - Low iPTM only (not low MW): {sorted(low_iptm - low_mw - OVERRIDES)}",
        f"  - Both low MW and low iPTM: {sorted(low_mw & low_iptm - OVERRIDES)}",
        f"  - Manual overrides: {sorted(OVERRIDES)}",
        "",
        "── AF3 compounds ──",
        "\n".join(sorted(af3_ids)),
        "",
        "── Fallback compounds ──",
        "\n".join(sorted(fallback_ids)),
    ]
    with open(os.path.join(OUT_DIR, "manifest.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")

    create_zip(OUT_DIR, "H6")
    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H7 — AF3+9fzj best-iPTM (high iPTM) + ICM 4D smaller-box ensemble (low iPTM + overrides)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H7():
    print("\n── Assembling H7 ──")

    IPTM_XLSX = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC  = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1")
    LOW_SRC   = os.path.join(ROOT, "methods/Ensemble_Docking/Docking_14-recs/ICM_4d-docking/Processed_Out_PDBs_smallerbox")
    OUT_DIR   = os.path.join(HYBRID_DIR, "H7_AF3-9fzj_hiiptm_ICM4d-smlbx_loiptm")
    THRESHOLD = 0.70
    OVERRIDES = {"x01358-1", "x03063-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (AF3+9fzj best-iPTM): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (ICM 4D smaller-box): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="AF3+9fzj best-iPTM")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="ICM 4D smaller-box")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H7")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H8 — AF3+9fzj best-iPTM (high iPTM) + ICM 4D smaller-box ensemble (iPTM<0.75 + overrides)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H8():
    print("\n── Assembling H8 ──")

    IPTM_XLSX = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC  = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1")
    LOW_SRC   = os.path.join(ROOT, "methods/Ensemble_Docking/Docking_14-recs/ICM_4d-docking/Processed_Out_PDBs_smallerbox")
    OUT_DIR   = os.path.join(HYBRID_DIR, "H8_AF3-9fzj_iptm0p75_ICM4d-smlbx_loiptm")
    THRESHOLD = 0.75
    OVERRIDES = {"x01358-1", "x03063-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (AF3+9fzj best-iPTM): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (ICM 4D smaller-box): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="AF3+9fzj best-iPTM")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="ICM 4D smaller-box")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H8")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# H9 — AF3+9fzj best-iPTM (high iPTM) + ICM 4D smaller-box ensemble (iPTM<0.80 + overrides)
# ══════════════════════════════════════════════════════════════════════════════

def assemble_H9():
    print("\n── Assembling H9 ──")

    IPTM_XLSX = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx")
    HIGH_SRC  = os.path.join(ROOT, "methods/AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1")
    LOW_SRC   = os.path.join(ROOT, "methods/Ensemble_Docking/Docking_14-recs/ICM_4d-docking/Processed_Out_PDBs_smallerbox")
    OUT_DIR   = os.path.join(HYBRID_DIR, "H9_AF3-9fzj_iptm0p80_ICM4d-smlbx_loiptm")
    THRESHOLD = 0.80
    OVERRIDES = {"x01358-1", "x03063-1"}

    os.makedirs(OUT_DIR, exist_ok=True)

    iptm = load_iptm(IPTM_XLSX)
    all_ids = set(iptm.keys())

    high_ids = {cid for cid, v in iptm.items() if v >= THRESHOLD and cid not in OVERRIDES}
    low_ids  = (all_ids - high_ids) | OVERRIDES

    print(f"  iPTM threshold: {THRESHOLD}")
    print(f"  High-iPTM (AF3+9fzj best-iPTM): {len(high_ids)}")
    print(f"  Low-iPTM + overrides (ICM 4D smaller-box): {len(low_ids)}")

    copy_structures(sorted(high_ids), HIGH_SRC, OUT_DIR, label="AF3+9fzj best-iPTM")
    copy_structures(sorted(low_ids),  LOW_SRC,  OUT_DIR, label="ICM 4D smaller-box")
    write_manifest(OUT_DIR, high_ids, low_ids, OVERRIDES,
                   high_src=HIGH_SRC, low_src=LOW_SRC)
    create_zip(OUT_DIR, "H9")

    print(f"  Output: {OUT_DIR}")


# ══════════════════════════════════════════════════════════════════════════════
# Add new submissions below following the same pattern
# ══════════════════════════════════════════════════════════════════════════════


# ── Entry point ────────────────────────────────────────────────────────────────

SUBMISSIONS = {"H1": assemble_H1, "H2": assemble_H2, "H3": assemble_H3, "H4": assemble_H4, "H5": assemble_H5, "H6": assemble_H6, "H7": assemble_H7, "H8": assemble_H8, "H9": assemble_H9}

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
