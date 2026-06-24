# Hybrid Submission Curation Log

Each submission is assembled by `assemble_submissions.py` under the corresponding
section. Update both this log and the script together when adding a new submission.

---

## H1 — AF3+9fzj Glide-redocked (high iPTM) + Boltz2+Glide confgen (low iPTM)

**Output folder:** `methods/Hybrid/H1_AF3-9fzj-glide_hiiptm_B2glide_loiptm/`

**Hypothesis:** Submission #34 (Glide redocking of AF3+9fzj predictions) underperformed
the raw AF3+9fzj predictions (#26) because low-iPTM and misplaced structures were
redocked from a bad starting pose, making them worse. This submission tests whether
using Glide-redocked poses only for high-confidence structures (iPTM ≥ 0.70) and
falling back to Boltz2+Glide confgen for the rest recovers the performance.

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.70): `Glide/5_AF3-w-9fzj-templ-iptm_redocking/docked_pdbs/`
- Low iPTM (< 0.70) + x01358: `Glide/2_Boltz2-rcy5-smpl300/docked_pdbs/`

**iPTM threshold:** 0.70

**Manual overrides:** x01358 (iPTM=0.73 but known bad pose — use fallback)

**Submitted:** Yes
**Result:** Rank 8/59, LDDT-PLI=0.5244, BiSyRMSD=3.818, LDDT-LP=0.9135 — worse than raw AF3+9fzj (#26). Glide redocking degrades good AF3 poses.

---

## H2 — Distance-based hybrid: AF3+9fzj (dist<8Å) + Boltz2+Glide confgen (dist≥8Å)

**Output folder:** `methods/Hybrid/H2_AF3-9fzj_dist-based_B2glide-fallback/`

**Hypothesis:** Use ligand distance from the 9fzj binding site (after Cα superposition)
as a direct criterion for pose quality, rather than iPTM as a proxy. AF3 poses within
8 Å of the reference binding site are kept; those further away are replaced by
Boltz2+Glide confgen poses. For compounds where both are >8 Å, Boltz2+Glide is
preferred as it is physically scored.

**Sources:**
- AF3 distances: `analysis/outlier_analysis/ligand_distances.csv`
- AF3 poses (dist < 8 Å): `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/`
- Fallback (dist ≥ 8 Å): `Glide/2_Boltz2-rcy5-smpl300/docked_pdbs/`

**Distance threshold:** 8.0 Å

**Submitted:** —
**Result:** —

---

## H3 — AF3+9fzj PrepWiz-prepared (high iPTM) + Boltz2+Glide confgen (low iPTM)

**Output folder:** `methods/Hybrid/H3_AF3-9fzj-prepwiz_hiiptm_B2glide_loiptm/`

**Hypothesis:** Same iPTM split as H1/H2, but for high-iPTM structures use the
PrepWiz-prepared AF3+9fzj poses (no redocking) instead of raw AF3 or Glide-redocked.
PrepWiz may fix small geometry issues (H-bonds, protonation, clashes) in the AF3
outputs without displacing the ligand. Low-iPTM fallback is Boltz2+Glide confgen
as in the best iPTM-based submissions (#51, #52).

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.70): `Glide/5_AF3-w-9fzj-templ-iptm_redocking/prepwizzed/`
- Low iPTM (< 0.70) + x01358: `Glide/2_Boltz2-rcy5-smpl300/docked_pdbs/`

**iPTM threshold:** 0.70

**Manual overrides:** x01358-1 (iPTM=0.73 but known bad pose — use fallback)

**Submitted:** —
**Result:** —

