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

**Submitted:** Yes (sub #54)
**Result:** Rank 15/60, LDDT-PLI=0.5023, BiSyRMSD=3.8541, LDDT-LP=0.9104 — worse than #52. Distance threshold too aggressive; only 4 compounds >10Å and 3 of those already had low iPTM. The 8Å cutoff pulled in-pocket but imperfect AF3 poses into the fallback unnecessarily.

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

**Submitted:** Yes (sub #55)
**Result:** Rank 5/60, LDDT-PLI=0.5329, BiSyRMSD=3.7049, LDDT-LP=0.9138 — better than H1/H2 but worse than raw #52. PrepWiz geometry fixes do not help; the raw AF3 poses in #52 are already better than PrepWiz-prepared ones.

---

## H4 — AF3+9fzj mininplace-minimized (high iPTM) + Boltz2+Glide confgen (low iPTM)

**Output folder:** `methods/Hybrid/H4_AF3-9fzj-mininplace_hiiptm_B2glide_loiptm/`

**Hypothesis:** Same iPTM split as H1/H3, but for high-iPTM structures use Glide
mininplace-minimized AF3+9fzj poses. Mininplace allows only local torsional
minimization within the binding site, so it may correct small clashes/geometry
issues in the AF3 poses without displacing the ligand — more conservative than
confgen redocking but more physically refined than raw AF3 or PrepWiz.
Low-iPTM fallback is Boltz2+Glide confgen as in #52.

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.70): `Glide/5_AF3-w-9fzj-templ-iptm_redocking/minimized_pdbs/`
- Low iPTM (< 0.70) + x01358-1: `Glide/2_Boltz2-rcy5-smpl300/docked_pdbs/`

**iPTM threshold:** 0.70

**Manual overrides:** x01358-1 (iPTM=0.73 but known bad pose — use fallback)

**Submitted:** Yes (sub #57)
**Result:** Rank 5/60, LDDT-PLI=0.5302, BiSyRMSD=3.7166, LDDT-LP=0.9127 — worse than #52 (0.5540). Mininplace minimization degrades AF3 poses; raw AF3 remains better than any Glide post-processing for high-iPTM structures.

---

## H5 — AF3+9fzj best-iPTM (high iPTM) + ICM-Pro Boltz2 docked (low iPTM)

**Output folder:** `methods/Hybrid/H5_AF3-9fzj_hiiptm_B2icm_loiptm/`

**Hypothesis:** Same as #52 but replace the Boltz2+Glide confgen fallback with
ICM-Pro docked Boltz2 poses. Sub #43 showed ICM 4D ensemble outperformed Glide
ensemble when used as a fallback for low-iPTM AF3 structures. Testing whether
ICM-docked Boltz2 poses also beat Glide-docked Boltz2 for the same ~15 compound
fallback set.

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.70): `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/`
- Low iPTM (< 0.70) + x01358-1: `ICM-Pro/2_Boltz2-rcy5-smpl300/docked_pdb_outs/`

**iPTM threshold:** 0.70

**Manual overrides:** x01358-1 (iPTM=0.73 but known bad pose — use fallback)

**Submitted:** Yes
**Result:** LDDT-PLI=0.5402, BiSyRMSD=3.6894, LDDT-LP=0.9135 — worse than #52 (0.5540). ICM-docked Boltz2 fallback underperforms Glide-docked Boltz2 for this low-iPTM subset, despite ICM outperforming Glide ensemble in #43 vs #37. Glide confgen remains the better fallback for these ~15 compounds.

---

## H6 — AF3+9fzj best-iPTM + Boltz2+Glide confgen (MW<250 OR iPTM<0.70 OR outlier)

**Output folder:** `methods/Hybrid/H6_AF3-9fzj_mw-iptm-outlier_B2glide-fallback/`

**Hypothesis:** Extend the #52 replacement criterion from iPTM-only to a union of three
conditions: low MW (< 250 Da, fragment rule-of-3 cutoff), low iPTM (< 0.70), or manual
outlier (x01358-1). The idea is that AF3 may be overconfident for small fragments —
reporting high iPTM but still producing poor poses — so MW provides an orthogonal
signal to catch those cases.

**Sources:**
- SMILES (for MW): `data/raw/pxr-challenge_structure_TEST_BLINDED.csv`
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- AF3 (high confidence, MW≥250, not outlier): `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/`
- Fallback: `Glide/2_Boltz2-rcy5-smpl300/docked_pdbs/`

**MW threshold:** 250 Da
**iPTM threshold:** 0.70
**Manual overrides:** x01358-1

**Submitted:** Yes (sub #59)
**Result:** Rank 24/73, LDDT-PLI=0.5061, BiSyRMSD=3.8454, LDDT-LP=0.9097 — much worse than #52 (0.5540). AF3 is NOT overconfident on high-iPTM fragments; replacing 75 compounds (vs 15 in #52) with docking massively hurts performance. MW alone is a poor criterion — iPTM is the better signal.

---

## H7 — AF3+9fzj best-iPTM (high iPTM) + ICM 4D smaller-box ensemble (low iPTM + overrides)

**Output folder:** `methods/Hybrid/H7_AF3-9fzj_hiiptm_ICM4d-smlbx_loiptm/`

**Hypothesis:** Same iPTM split as #60, but use ICM 4D smaller-box ensemble docking
(sub #39) as the fallback instead of Boltz2+Glide confgen. Sub #39 outperformed
the original ICM 4D box (#38) for standalone docking. The blind half of the
leaderboard is all larger compounds, where ICM's 4D ensemble sampling across 14
receptor conformations may generalize better than Glide confgen. Overrides include
both x01358-1 and x03063-1 (as in #60).

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.70): `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/`
- Low iPTM (< 0.70) + overrides: `Ensemble_Docking/Docking_14-recs/ICM_4d-docking/Processed_Out_PDBs_smallerbox/`

**iPTM threshold:** 0.70
**Manual overrides:** x01358-1, x03063-1

**Submitted:** Yes (sub #61)
**Result:** Rank 19/94, LDDT-PLI=0.5513, BiSyRMSD=3.6091, LDDT-LP=0.9133 — slightly worse than #60 (0.5536). Boltz2+Glide confgen remains the better fallback over ICM 4D smaller-box for the low-iPTM set.

---

## H8 — AF3+9fzj best-iPTM + ICM 4D smaller-box (iPTM<0.75 + overrides)

**Output folder:** `methods/Hybrid/H8_AF3-9fzj_iptm0p75_ICM4d-smlbx_loiptm/`

**Hypothesis:** Same as H7 but with a wider replacement threshold (0.75 instead of 0.70),
replacing more borderline-confidence AF3 structures with ICM 4D smaller-box poses.
Testing whether the 0.70–0.75 iPTM range is better served by ICM docking,
particularly for the blind (larger compound) half of the dataset.

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.75): `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/`
- Low iPTM (< 0.75) + overrides: `Ensemble_Docking/Docking_14-recs/ICM_4d-docking/Processed_Out_PDBs_smallerbox/`

**iPTM threshold:** 0.75
**Manual overrides:** x01358-1, x03063-1

**Submitted:** Yes (sub #62)
**Result:** Rank 25/94, LDDT-PLI=0.5407, BiSyRMSD=3.8360, LDDT-LP=0.9113 — worse than #60. Wider threshold pulls in too many good AF3 poses for ICM to replace.

---

## H9 — AF3+9fzj best-iPTM + ICM 4D smaller-box (iPTM<0.80 + overrides)

**Output folder:** `methods/Hybrid/H9_AF3-9fzj_iptm0p80_ICM4d-smlbx_loiptm/`

**Hypothesis:** Same as H7/H8 but with an even wider threshold (0.80), replacing all
lower-confidence AF3 structures with ICM 4D smaller-box poses. Tests the upper bound
of how far the ICM fallback can be extended before it starts replacing genuinely good
AF3 poses.

**Sources:**
- iPTM values: `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/results.xlsx`
- High iPTM (≥ 0.80): `AlphaFold3/2_w-9fzj-template/best-iptm_PDB_outs1/`
- Low iPTM (< 0.80) + overrides: `Ensemble_Docking/Docking_14-recs/ICM_4d-docking/Processed_Out_PDBs_smallerbox/`

**iPTM threshold:** 0.80
**Manual overrides:** x01358-1, x03063-1

**Submitted:** —
**Result:** —
