# PXR Structure Prediction Challenge

Submissions for the **Structure Prediction Track** of the [OpenADMET PXR Challenge](https://huggingface.co/spaces/openadmet/pxr-challenge?ref=openadmet.ghost.io) — a blind challenge to predict protein-ligand complex structures of the human Pregnane X Receptor (PXR) with 184 diverse ligands.

---

## The Challenge

The goal is to predict the 3D structure of PXR bound to each ligand in the challenge set, evaluated against experimentally determined structures using three metrics:

| Metric | Meaning | Better |
|---|---|---|
| **LDDT-PLI** | Local distance difference test at the protein-ligand interface | Higher |
| **BiSyRMSD** | Binding site symmetry-corrected RMSD | Lower |
| **LDDT-LP** | LDDT for the ligand pose | Higher |

The challenge was released in two phases: an initial set of **78 compounds**, followed by the full set of **184 compounds**. All results below are for the 184-compound set.

---

## Approach & Key Findings

The overarching strategy was to systematically compare **AI-based co-folding** (AlphaFold3, Boltz2) against **classical docking** (Glide, ICM-Pro), and to explore how template choice, pose selection, and ensemble strategies affect prediction quality.

### Co-folding outperforms docking into a single fixed receptor

Early submissions used a single AF3-server-predicted PXR structure as a rigid receptor for docking all 184 ligands. These performed poorly (rank ~10–21/27 at the time). Switching to co-folding — predicting a unique protein-ligand complex for each ligand — gave a significant improvement.

### AlphaFold3 outperforms Boltz2

Despite extensive Boltz2 experimentation (varying MSA sources, recycling steps, sampling steps, PDB templates, and energy potentials), AF3 consistently produced better predictions. The best Boltz2 submission achieved rank 3/20; the best AF3-only submission achieved rank 3/30 with a notably higher LDDT-PLI (0.5055 vs 0.4735).

### Selecting the best-iPTM prediction improves over AF3's default ranking

AF3 generates 5 candidate structures per compound and ranks them by an internal score. Replacing AF3's default best with the structure having the highest **iPTM** (interface predicted TM-score, a measure of interface confidence) consistently improved results. For the 9fzj-template run, this improved the rank from 4/36 to 3/50, and LDDT-PLI from 0.5104 to 0.5285.

### Template choice matters: 9fzj is the best single template

Among the PDB templates tested (4ny9, 7axe, 9fzj), using **9fzj** as the structural template for AF3 co-folding gave the best results. The best-iPTM AF3+9fzj submission became the foundation for all subsequent hybrid strategies.

### Hybrid strategy: replace low-confidence predictions with ensemble docking

The current best submission combines AF3+9fzj best-iPTM predictions with ensemble docking results for low-confidence structures. For compounds where iPTM < 0.70, the AF3 prediction is replaced by the best-scoring pose from **ICM-Pro 4D ensemble docking** across 14 diverse PXR receptors. This hybrid achieves the best overall performance (rank 4/56, LDDT-PLI=0.5488, BiSyRMSD=3.8158).

---

## Results Summary

Selected submissions for the 184-compound set (ranked by current leaderboard position):

| Sub. | Rank | LDDT-PLI | BiSyRMSD | LDDT-LP | Method |
|------|------|----------|----------|---------|--------|
| 43 | 4/56 | 0.5488 | 3.8158 | 0.9132 | AF3+9fzj best-iPTM; iPTM<0.70 → ICM 4D ensemble |
| 44 | 4/56 | 0.5407 | 3.8360 | 0.9113 | AF3+9fzj best-iPTM; iPTM<0.75 → ICM 4D ensemble |
| 41 | 4/56 | 0.5298 | 3.8268 | 0.9018 | AF3+9fzj best-iPTM; iPTM<0.75 → Glide ensemble |
| 37 | 4/55 | 0.5380 | 3.9148 | 0.9039 | AF3+9fzj best-iPTM; iPTM<0.70 → Glide ensemble |
| 26 | 3/50 | 0.5285 | 4.5284 | 0.9152 | AF3+9fzj best-iPTM |
| 36 | 9/55 | 0.5132 | 4.6579 | 0.9128 | AF3+7axe best-iPTM |
| 27 | 9/50 | 0.4971 | 4.7661 | 0.9173 | AF3+template search, best-iPTM |
| 18 | 3/30 | 0.5055 | 4.7035 | 0.9149 | Plain AF3, default best |
| 13 | 3/20 | 0.4954 | 3.9243 | 0.9082 | Boltz2 (rcy=5, smpl=300) + Glide confgen |
| 35 | 40/55 | 0.4266 | 4.7670 | 0.8872 | 14-receptor Glide ensemble docking |
| 38 | 52/56 | 0.3145 | 6.5166 | 0.8958 | 14-receptor ICM 4D ensemble docking |

> **Note:** The challenge is ongoing. Rankings will change as more teams submit.

---

## Methods

### Co-folding

#### AlphaFold3
All 184 compounds co-folded with the full PXR sequence using a ColabFold-generated MSA. Five candidate structures are generated per compound; the best is selected either by AF3's internal ranking or by highest iPTM across all 5 candidates.

| Folder | Template Strategy |
|---|---|
| `1_plain_AF3` | No template |
| `2_w-4ny9-template` | PDB 4ny9 as fixed template |
| `2_w-7axe-template` | PDB 7axe as fixed template |
| `2_w-9fzj-template` | PDB 9fzj as fixed template |
| `3_w-templ-search` | AF3 automatic template search |
| `5_9fzj-templ_multiseed` | PDB 9fzj, multiple seeds *(in progress)* |

#### Boltz2
All 184 compounds co-folded using various MSA sources, PDB templates, and inference parameters.

| Folder | Configuration |
|---|---|
| `1_*` | Default settings, ColabFold MSA |
| `2_*` | ColabFold MSA, `--recycling_steps 5 --sampling_steps 300` |
| `3_*` | ColabFold MSA, `--recycling_steps 6 --sampling_steps 400` |
| `4_*` | 3 PDB templates + ColabFold MSA |
| `5_*` | 3 PDB templates + ColabFold MSA + `--use_potentials` |

### Docking

All docking experiments use a rigid receptor. Three redocking strategies were applied to co-folding outputs:
- **PrepWiz only** — prepare the co-folded complex with Schrödinger PrepWizard, no redocking
- **Minimization** — minimize the ligand in place using Glide `mininplace`
- **Redocking** — fully redock the ligand into its respective receptor using Glide `confgen`

#### Glide (Schrödinger)

| Folder | Description |
|---|---|
| `1_singleAF3_model` | Single AF3-server receptor, all 184 ligands docked |
| `2_Boltz2-rcy5-smpl300` | Redocking into Boltz2 predictions |
| `3_plainAF3_redocking` | Redocking into plain AF3 predictions |
| `4_AF3-w-templ-search_redocking` | Redocking into AF3+template search predictions |
| `5_AF3-w-9fzj-templ-iptm_redocking` | Redocking into AF3+9fzj best-iPTM predictions |
| `6_Single-receptor-9fzj` | Single experimental PDB 9fzj receptor, all 184 ligands docked |

#### ICM-Pro (Molsoft)

| Folder | Description |
|---|---|
| `0_AF3_model` / `1-1_AF3_model` | Single AF3-server receptor, all 184 ligands docked |
| `2_Boltz2-rcy5-smpl300` | Redocking into Boltz2 predictions |
| `3_plainAF3_redocking` | Redocking into plain AF3 predictions |
| `4_Single-receptor-9fzj` | Single experimental PDB 9fzj receptor, all 184 ligands docked |

### Ensemble Docking

60+ experimental PXR PDB structures were clustered in ICM-Pro and one representative from each cluster was selected, yielding **14 diverse receptors**. All 184 ligands were docked into all 14 receptors using both Glide and ICM-Pro 4D docking. For each ligand, the receptor+pose with the best docking score across all 14 receptors was selected for submission.

---

## Repository Structure

```
pxr-structure-challenge/
├── data/
│   ├── raw/                  # PDB/CIF template structures, MSA files,
│   │                         # template JSON/YAML files, compound CSVs
│   ├── processed/
│   │   ├── af3_jsons/        # Per-compound AF3 input JSONs (184 per experiment)
│   │   └── boltz2_yamls/     # Per-compound Boltz2 input YAMLs
│   └── scripts/
│       ├── create_jsons.py   # Generate AF3 JSONs from CSV + template
│       └── create_yamls.py   # Generate Boltz2 YAMLs from CSV + template
│
├── methods/
│   ├── AlphaFold3/           # Co-folding results and scripts
│   ├── boltz2/               # Co-folding results and scripts
│   ├── Glide/                # Docking results and scripts
│   ├── ICM-Pro/              # Docking results and scripts
│   ├── Vina/                 # AutoDock Vina scripts
│   └── Ensemble_Docking/     # 14-receptor ensemble docking results
│
└── slurm/                    # SLURM job submission scripts
```

---

## Environment & Dependencies

```bash
conda env create -f environment.yml
conda activate boltz
```

External tools required (HPC modules or local installs):
- [AlphaFold3](https://github.com/google-deepmind/alphafold3)
- [Boltz2](https://github.com/jwohlwend/boltz)
- [Schrödinger Suite](https://www.schrodinger.com/) (PrepWizard, Glide)
- [Molsoft ICM-Pro](https://www.molsoft.com/icm_pro.html)
- [ColabFold](https://github.com/sokrypton/ColabFold) (for MSA generation)

---

## Citation / Challenge

OpenADMET PXR Structure Prediction Challenge:
https://huggingface.co/spaces/openadmet/pxr-challenge
