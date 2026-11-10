# MOD550 — Assignment 3

**Engineering Machine Learning with Real-World Data**
Part I: Support Vector Machine classification · Part II: Deep learning (1-D CNN)

**Student:** Aditya Borah
**Submitted:** *(date)*
**Working version:** v5 (see [Version history](#version-history))

---

## What this assignment does

Both parts classify **rolling-element bearing faults** from vibration measured on the Case
Western Reserve University bearing test rig. From 0.17 s of drive-end acceleration the task
is to name the fault's **location** (ball, inner race, outer race) *and* its **severity**
(0.007", 0.014", 0.021"), or report that the bearing is healthy: ten classes in all.

Part I does it from 33 hand-engineered features with SVMs. Part II gives a 1-D CNN the raw
waveform. Both use the **same windows and the same split**, so the two results are directly
comparable.

Beyond the required analysis, each task also works through the standard checks for its
method on this same data (scaling, leakage, kernels and their hyperparameters, metrics,
convolution and parameter counting, pooling, augmentation and more). They sit inside the
tasks they belong to; see [Methods and where they are](#methods-and-where-they-are).

### Headline results — held-out 3 hp motor load, 827 windows

| Model | Input | macro-F1 |
|---|---|---|
| SVM, linear kernel | 33 engineered features | **0.8809** |
| Random forest | 33 engineered features | 0.8779 |
| **1-D CNN** (mean of 5 seeds) | raw 2048-sample window | **0.8663** ± 0.1156 *(range 0.7345–0.9932)* |
| SVM, RBF kernel | 33 engineered features | 0.8454 |
| SVM, polynomial (d=3) | 33 engineered features | 0.8045 |
| Logistic regression | 33 engineered features | 0.8030 |

Three findings are worth more than the ranking:

1. **The split is the result.** Splitting the same windows at random instead of by motor
   load takes the same model from 0.845 to **0.994**, because 100% of the randomly chosen
   test windows come from a recording that is also in training.
2. **The CNN and the SVM are not distinguishable on average**, but they are on
   *reproducibility*. Their means differ by 0.015; the CNN's own spread across five random
   seeds is 0.259, **17.7× larger**. Two of five seeds beat the best SVM. Refit the SVM and
   you get the same classifier; retrain the CNN and you may get 0.73 or 0.99, with the
   validation set reporting a flawless 1.000 either way.
3. **Detection is solved; severity is not.** No model in either part ever calls a faulty
   bearing healthy (0 of 768). Essentially all remaining error is severity confusion, and it
   was predicted before any model was fitted; see Task I.2.6.

---

## Dataset

**Case Western Reserve University Bearing Data Center — Seeded Fault Test Data**
<https://engineering.case.edu/bearingdatacenter>

| | |
|---|---|
| **Rig** | 2 hp Reliance Electric motor, torque transducer, dynamometer |
| **Test bearing** | SKF 6205-2RS JEM deep-groove ball bearing (drive end) |
| **Faults** | single-point defects cut by EDM at 0.007", 0.014", 0.021" on inner race, ball, outer race |
| **Loads** | 0, 1, 2, 3 hp; shaft speeds 1797 to 1725 rpm |
| **Channel used** | drive-end accelerometer, 12 kHz |
| **Recordings used** | 56 files, 564 s of vibration, 187 MB (list in [The data](#the-data-data-folder)) |
| **Windows** | 3275 non-overlapping windows of 2048 samples (0.171 s) |
| **Classes** | 10: `Normal` + {`Ball`, `Inner`, `Outer`} × {`007`, `014`, `021`} |
| **Imbalance** | 3.4 : 1 (`Outer_007` and `Outer_021` 708 windows, `Normal` 206) |

**Licence and permissions.** The Bearing Data Center publishes the files for free public
download and asks that the source be acknowledged in work that uses them; it places no
licence fee or redistribution charge on academic use. This repository therefore **does not
redistribute the data** (it is 187 MB, over the assignment's ~50 MB limit): the exact file
list and where to get it are in [The data](#the-data-data-folder), and the citation above is
reproduced in both notebooks.

**Two things about this data that the notebooks handle explicitly** (both found during
exploration, both documented in Task I.2):

- The **healthy baseline recordings were sampled at 48 kHz**, not the 12 kHz of the fault
  recordings. Left uncorrected, any model can identify the healthy class from its sampling
  rate rather than from the bearing. They are decimated 48 → 12 kHz with an anti-alias
  filter.
- **`Normal/99_Normal_2.mat` ships a stray copy of the previous record's variables**
  (`X098_*` alongside `X099_*`). Selecting "the first key ending in `DE_time`" silently loads
  the 1 hp baseline in place of the 2 hp one, which, with a load-wise split, puts a
  byte-identical copy of a training recording into the validation set. `read_mat` (in each
  notebook's "Reading the data" cell) resolves the channel by the file's own record number; the duplicate-window check in
  Task I.2.3 is what catches it if this ever regresses.

---

## Repository layout

```
MOD550_Assignment_3/
├── Part_I_SVM.ipynb               Part I: SVM classification (run this first)
├── Part_II_Deep_Learning.ipynb    Part II: 1-D CNN
├── README.md
├── requirements.txt
├── Data/                          the 56 .mat files: not committed, downloaded on first run (see "The data")
├── models/                        written by Part II (saved Keras model + scaling constants)
├── figures/                       written by the notebooks
└── results/                       written by the notebooks (CSV)
```

There is **no `scripts/` folder and nothing is imported between files**. Both notebooks begin
with the same two setup cells: one for the imports and plot style, and one, "Reading the
data", that reads the recordings straight from `Data/`, resamples the healthy baseline,
cuts the windows and defines the split. Because the cell is identical in both notebooks,
Part I and Part II are fitted and scored on exactly the same windows, so the comparison in
Task II.3 is between models rather than between pipelines. Part I writes its test
predictions to `results/part1_test_predictions.csv`, and Part II reloads them and asserts
that the test labels match before comparing. The 33 features are computed inside Part I
itself (Task I.2.5), where the assignment expects to see them.

---

## The data (`Data/` folder)

The notebooks read the recordings from a folder called `Data` next to them. **If the folder
or any of the files are missing, the "Reading the data" cell downloads exactly the missing
ones, once** (about 187 MB for all 56, roughly a minute on a normal connection), and every
later run reads them locally without touching the network. Nothing needs to be installed or
run beforehand. Run from the project folder (VS Code and Jupyter do this by default when the
notebook is opened from there). Each file is tried from the Bearing Data Center first and,
if that fails, from a public mirror of the same recordings, and is only kept if it opens as a
proper recording. `AUTO_DOWNLOAD = False` at the top of that cell switches the download off
(a missing file then stops the notebook with the list of missing file numbers).

**Which files.** 56 of the files on the CWRU Bearing Data Center site, named by file number
exactly as the site names them (`105.mat`, `130.mat`, ...). Any name that *starts with* the
file number also works (`105_0.mat`), and sub-folders inside `Data/` are fine.

*Normal Baseline Data page* (48 kHz, decimated to 12 kHz by the notebook): files
**97, 98, 99, 100**, for loads 0, 1, 2, 3 hp.

*12k Drive End Bearing Fault Data page* (12 kHz): the 52 files below, for loads 0, 1, 2, 3 hp.

| Fault | Diameter | Outer-race position | 0 hp | 1 hp | 2 hp | 3 hp |
|---|---|---|---|---|---|---|
| Ball | 0.007" | n/a | 118 | 119 | 120 | 121 |
| Ball | 0.014" | n/a | 185 | 186 | 187 | 188 |
| Ball | 0.021" | n/a | 222 | 223 | 224 | 225 |
| Inner race | 0.007" | n/a | 105 | 106 | 107 | 108 |
| Inner race | 0.014" | n/a | 169 | 170 | 171 | 172 |
| Inner race | 0.021" | n/a | 209 | 210 | 211 | 212 |
| Outer race | 0.007" | @6 | 130 | 131 | 132 | 133 |
| Outer race | 0.007" | @3 | 144 | 145 | 146 | 147 |
| Outer race | 0.007" | @12 | 156 | 158 | 159 | 160 |
| Outer race | 0.014" | @6 | 197 | 198 | 199 | 200 |
| Outer race | 0.021" | @6 | 234 | 235 | 236 | 237 |
| Outer race | 0.021" | @3 | 246 | 247 | 248 | 249 |
| Outer race | 0.021" | @12 | 258 | 259 | 260 | 261 |

**Not used:** the 0.028" ball and inner-race files (3001 to 3008, excluded so that all three
fault types share the same three severities), and every other page of the site (48k Drive
End, Fan End, base accelerometer).

**Getting them by hand instead** (no internet during the run, or you prefer to fetch them yourself):

- *Fastest:* unzip `MOD550_Data_v5.zip` into the project folder; it creates `Data/` with the
  56 files in it, plus `FILES_NEEDED.csv` listing every file and its link. It was built from the copies this project was developed on (taken from the
  public mirror cited at the bottom), so for strict provenance use the next option.
- *From the source:* download the 56 files from the Bearing Data Center. Each link on the
  site is `https://engineering.case.edu/sites/default/files/<number>.mat`, so for example
  file 105 is `https://engineering.case.edu/sites/default/files/105.mat`. Put them all in
  `Data/`.

**Check.** Running the "Reading the data" cell finds the folder and the files, downloading
any that are missing. If a download fails (no internet, or both sources unreachable) it stops
and lists the missing file numbers. When everything is there, Task I.2.1
reports 56 recordings and Task I.2.3 reports 0 duplicated windows.

`Data/` is in `.gitignore`: it is 187 MB and the assignment asks that raw data over ~50 MB is
not committed and that a download script or instructions are provided instead. The download
cell and this section are those.

---

## Running it

```bash
# 1. dependencies  (Python 3.11+)
pip install -r requirements.txt

# 2. the data: nothing to do. The first run downloads it into Data/ (see "The data" above)

# 3. the notebooks, in this order
jupyter lab Part_I_SVM.ipynb
jupyter lab Part_II_Deep_Learning.ipynb
```

Or non-interactively:

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 Part_I_SVM.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 Part_II_Deep_Learning.ipynb
```

**Order matters.** Part II reads `results/part1_test_predictions.csv`, so Part I must run
first (the file is also committed, so Part II still runs if you start there). All paths are
relative to the project folder.

**Moving sections around.** Each notebook only depends on its two setup cells, which must run
first, and on the sections above a given cell having defined what it uses. Nothing is imported
from another file, so there is no path to break. If a cell fails with `NameError`, a section
that creates that object has been moved below the one using it. The objects each task hands
on are: Task I.2 builds `X, y, meta, F, Xf`; Task I.3 builds `tr, va, te, Xtr, Xva, Xte`;
Task I.4 builds `GRIDS, make_svm, rows`; Task I.5 builds `models, pred`. In Part II, Task
II.1 builds `X, y, meta, tr, va, te`, II.2.1 builds `Xtr, Xva, Xte, mu, sd`, II.2.2 builds
`build_cnn`, and Task II.3 builds `train_cnn`.

**Runtimes** (4-core CPU, no GPU): Part I about **1.5 min**. Part II about **15 to 17 min**,
almost all of it network training (the seed-stability and capacity studies, and the
label-format, validation-scheme, pooling and augmentation comparisons). No GPU is needed or
used.

---

## Methods and where they are

Each method is a numbered sub-section inside the task it belongs to. The cells that make up
the word-limited reports are the ones headed with their word count (Task I.3, the *Discussion*
of I.4, the *Critical analysis* of I.5, and II.1); the sub-sections hold the code, figures
and tables around them, and each notebook closes the sub-sections of its last task with a one-page summary table
(`results/part1_method_summary.csv`, `results/part2_method_summary.csv`).

| Section | Method |
|---|---|
| I.2.8 | last look at the feature table: shapes, class counts, missing, infinite, duplicated |
| I.3.1 | scaling: feature spread, the two scalers, fit on the training windows only |
| I.3.2 | identifier and constant columns that must not become features |
| I.3.3 | `stratify=y` and what an unstratified split does to the rarest class |
| I.3.4 | Tobler's law, semivariogram, correlogram and range of the window sequence |
| I.3.5 | the near-duplicate leak, and why accuracy alone is not a result |
| I.4.1 to I.4.3 | `kernel`, `C` and `gamma`, drawn on two bearing features and measured on all 33 |
| I.4.4 | choosing `C` and `gamma` without cheating: `cv=5` against leave-one-load-out |
| I.5.1 | `class_weight`: what a mistake costs |
| I.5.2 to I.5.5 | confusion matrix, metrics by hand, per-class and macro scores, `scoring=` |
| II.2.1 | checking the arrays before building a network |
| II.2.3 to II.2.8 | dense versus convolution, what a kernel does, padding and stride, parameters by hand, pooling, the shape of the whole network |
| II.3.3 to II.3.4 | one-hot against integer labels; the training knobs and why `validation_split` fails here |
| II.3.5 to II.3.6 | an unweighted run and its worst confusions; saving and reloading the model |
| II.4.1 | augmentation and dropout, with three seeds per setting |
| II.4.2 | one brand new measurement, end to end, through three acquisition chains |

**Four findings argue against common defaults. Only the first argues against a choice a task
made.** All four are reported rather than quietly fixed, so the tasks still describe what was
actually run:

1. **`class_weight="balanced"` is the wrong default here** (I.5.1, a choice made in Task I.4).
   It costs about 0.06 macro-F1 (0.908 without it, 0.845 with it) and protects nothing:
   `Normal` recall is 1.000 either way, while `Ball_021` recall falls from 0.661 to 0.254. The
   rare class was never the problem, so weighting by frequency aims the correction at the
   wrong target. For that reason the second set of CNN runs in Part II (II.3.5 onwards) is
   trained without `class_weight` and is not interchangeable with Task II.3's model.
2. **Fitting the scaler on all data gains 0.12 macro-F1** (I.3.1). The tasks already fit the
   scaler inside a `Pipeline`, so this measures what the shortcut would have cost, and the
   two scalers differ by only 2% in the median feature. A score that moves that far under a
   2% preprocessing change should not be quoted to three decimals.
3. **`validation_split=0.1` fails badly here** (II.3.4). It takes the *last* 10% rather than a
   random 10%, and our windows are ordered by recording, so it holds back a single class and
   reports validation accuracy 0.000. Shuffled first it reports a flattering 0.687, because
   those windows share recordings with training. Task II.3 validates on a held-out motor
   load, which avoids the trap.
4. **`GridSearchCV(cv=5)` claims 0.999 and delivers 0.879** (I.4.4). Leave-one-load-out also
   overstates (it claims 0.989 and delivers 0.845), but KFold's claim is the less believable,
   because it scores each fold on windows whose neighbours it has just trained on.

**How the test load is used.** The 3 hp load never selects a feature, a kernel or a
hyperparameter. Test-load scores that appear before Task I.5 (the leak measurement in I.3 and
a few illustrations in I.3 to I.4) only show what a practice costs; each section says so.

The variogram section (I.3.4) turns an assertion into a measurement. Three of four recordings
are effectively independent one window apart, but `OR_021 @6 o'clock` correlates 0.56 at lag
1 with a range of six windows, about a second of signal. A random split cannot know which
recordings behave which way, which is why splitting by recording is the only safe choice.

### Reproducibility

- `SEED = 42` throughout; `keras.utils.set_random_seed` is called inside `build_cnn` and
  `build_cnn_flex`.
- **The split involves no randomness at all**: it is defined by motor load, so it does not
  depend on the seed.
- Part II's conclusions rest on 5 seeds (stability) and 3 seeds × 4 widths (capacity),
  because the whole point of that section is that single-seed results here are not stable.
- TensorFlow on CPU may reorder floating-point reductions between runs, so the last decimal
  of a CNN number can move. `tf.config.experimental.enable_op_determinism()` fixes this at
  roughly double the runtime; it is left off deliberately.

### Dependencies

| Package | Version used |
|---|---|
| python | 3.13 |
| numpy | 2.5.3 |
| pandas | 3.0.5 |
| scipy | 1.18.1 |
| scikit-learn | 1.9.1 |
| matplotlib | 3.11.2 |
| tensorflow | 2.21.0 |

---

## Group-member contributions

> **Fill this in before submitting.** The group sections of both notebooks are shared work;
> the Individual Analysis sections are not.

| Member | Contribution |
|---|---|
| *(name)* | *(e.g. dataset selection, feature engineering, Task I.2 figures)* |
| *(name)* | *(e.g. SVM tuning and Task I.4)* |
| Aditya Borah | *(your own contribution)* |

Every member's `Individual Analysis` section contains only that member's independently
written answers, as required.

---

## AI usage log

> **Required by the assignment's AI policy, and this is the honest version; edit it to
> match what you actually did before you submit.** The policy permits AI for code, debugging
> and figures, requires it to be logged here, and requires that *all written analysis be your
> own* and that you be able to explain any line you submit.

| Tool | Used for | Kept / changed |
|---|---|---|
| Claude (Anthropic) | Dataset selection; the data-reading cell that both notebooks contain; feature-extraction code; all modelling and plotting code in both notebooks; the CNN architecture; the draft group-section commentary | Code kept and executed as written. **The group-section prose is a draft that must be read, checked and rewritten where you disagree with it.** |
| Claude (Anthropic) | The additional checks placed inside the tasks (I.2.8, I.3.1 to I.3.5, I.4.1 to I.4.4, I.5.1 to I.5.6, II.2.3 to II.2.8, II.3.3 to II.3.6, II.4.1 to II.4.3): code, figures and commentary | Code kept and executed. Same rule: the commentary is a draft to be read and owned before submission. |
| Claude (Anthropic) | Diagnosing the `99_Normal_2.mat` duplicate-channel bug after the duplicate-window check flagged 59 duplicates | Fix kept; the regression check was retained in the notebook |
| n/a | **Individual Analysis sections (Part I Q1–3, Part II Q1–3)** | **Not AI-written. These are left as evidence summaries plus `*Write your answer here.*` placeholders and must be written by you.** |

---

## Submission checklist

Deadline: **23:59, Friday 20 November 2026**. In order:

- [ ] **1. Get it running.** `pip install -r requirements.txt`, then run `Part_I_SVM.ipynb` and `Part_II_Deep_Learning.ipynb` in that order, start to
      finish, from a clean kernel. Confirm Part I's duplicate check still reports **0**.
- [ ] **2. Read both notebooks end to end, every numbered sub-section included.** You have
      to be able to explain any line you submit. Anything you cannot defend, change or
      delete.
- [ ] **3. Agree the group sections with your group.** Tasks I.1–I.5 and II.1–II.4 may be
      identical across members' repositories. Settle who did what.
- [ ] **4. Write the six Individual Analysis answers yourself**: Part I Q1–3 and Part II
      Q1–3, max 300 words each. They currently hold evidence tables and
      `*Write your answer here.*` placeholders, deliberately. **Near-identical answers
      within a group are graded as one submission and every member receives zero for that
      question.** Do not pass these around.
- [ ] **5. Put your full name in both Individual Analysis headings** and fill in the
      group-member table and AI log above.
- [ ] **6. Check the word limits:** Task I.1 ≤ 350, I.3 ≤ 200, I.4 ≤ 300, I.5 ≤ 300,
      II.1 ≤ 100, and each individual answer ≤ 300. The limits apply to the reports, which are
      the cells headed with their word count, not to the code, figures and tables of the
      numbered sub-sections around them.
- [ ] **7. Re-run both notebooks one last time** so the committed outputs match the
      committed code, and confirm cell numbering runs 1..n in order.
- [ ] **8. Push to your own GitHub repository**: one per student, containing both
      notebooks, this README and `requirements.txt`. Confirm `Data/` is **not** committed (it
      is in `.gitignore`; the assignment caps committed data at ~50 MB and this is 187 MB).
- [ ] **9. Clone your own repo somewhere fresh and run it** (without `Data/`, so the download
      is exercised) to prove the relative paths and the data download work for someone who is
      not you.

---

## Citation

> Case Western Reserve University Bearing Data Center. *Seeded Fault Test Data*.
> <https://engineering.case.edu/bearingdatacenter> (accessed November 2026).
> The copies the reported numbers were produced from came via the public mirror
> <https://github.com/s-whynot/CWRU-dataset>; the same files are on the site above.

Further reading on this dataset's quirks, not relied on for any claim made above (the
anomalies in Task I.2 were found in the data itself, not taken from the literature):

> W. A. Smith and R. B. Randall, "Rolling element bearing diagnostics using the Case Western
> Reserve University data: A benchmark study," *Mechanical Systems and Signal Processing*,
> vol. 64–65, pp. 100–131, 2015. doi:10.1016/j.ymssp.2015.04.021

---

## Version history

*(Working notes for the group. Delete this section before submitting.)*

| Version | What changed |
|---|---|
| v1 | Part I and Part II first complete versions; data fetched by `scripts/download_data.py`, shared loader in `scripts/cwru_data.py` |
| v2 | added a third notebook, `Part_III_Course_Methods.ipynb` |
| v3 | Part III deleted; its methods added at the end of Part I and of Part II |
| v4 | **data read directly from a local `Data/` folder; `scripts/` removed and nothing imported between files; those end-of-notebook additions moved into the tasks they belong to as ordinary numbered sub-sections, with every reference to where the methods came from removed**; two sentences in I.4 and I.5 reworded so the claims about the test load stay true (I.3 already prints a test-load score for the leak measurement); four 0.014" outer-race recordings now carry their true clock position (`@6`); the saved model gets a `bearing_cnn_scaling.json` beside it |
| v5 | the "Reading the data" cell downloads any missing recordings into `Data/` on the first run (official site first, public mirror as fallback), so the notebooks run without any manual data step; everything else as v4 |
