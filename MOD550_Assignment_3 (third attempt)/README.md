# MOD550 — Assignment 3

**Engineering Machine Learning with Real-World Data**
Part I: Support Vector Machine classification · Part II: Deep learning (1-D CNN)

**Submitted:** *(date)*

---

## What this assignment does

Both parts classify **rolling-element bearing faults** from vibration measured on the Case
Western Reserve University bearing test rig. From 0.17 s of drive-end acceleration the task
is to name the fault's **location** (ball, inner race, outer race) *and* its **severity**
(0.007", 0.014", 0.021"), or report that the bearing is healthy: ten classes in all.

Part I does it from 33 hand-engineered features with SVMs. Part II gives a 1-D CNN the raw
waveform. Both use the **same windows and the same split**, so the two results are directly
comparable.

Each notebook also ends with a clearly labelled **supplement** that works through every
method taught in the MOD550 labs (SVM lab, spatial-statistics lecture, CNN lab) on this same
data. See [Course-lab supplements](#course-lab-supplements) below.

### Headline results — held-out 3 hp motor load, 827 windows, scored once

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
| **Recordings used** | 56 files, 564 s of vibration, ~195 MB |
| **Windows** | 3275 non-overlapping windows of 2048 samples (0.171 s) |
| **Classes** | 10: `Normal` + {`Ball`, `Inner`, `Outer`} × {`007`, `014`, `021`} |
| **Imbalance** | 3.4 : 1 (`Outer_007` and `Outer_021` 708 windows, `Normal` 206) |

**Licence and permissions.** The Bearing Data Center publishes the files for free public
download and asks that the source be acknowledged in work that uses them; it places no
licence fee or redistribution charge on academic use. This repository therefore **does not
redistribute the data**: `scripts/download_data.py` fetches it, and the citation above is
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
  byte-identical copy of a training recording into the validation set. `cwru_data._read_mat`
  resolves the channel by the file's own record number; the duplicate-window check in
  Task I.2.3 is what catches it if this ever regresses.

---

## Repository layout

```
MOD550_Assignment_3/
├── Part_I_SVM.ipynb               Part I: SVM classification (run this first)
├── Part_II_Deep_Learning.ipynb    Part II: 1-D CNN
├── README.md
├── requirements.txt
├── scripts/
│   ├── download_data.py          fetches the .mat files (data is not committed)
│   └── cwru_data.py              shared data layer: loading, resampling, windowing, split
├── data/                         created by download_data.py, not committed
│   ├── Normal/                                    4 .mat files
│   └── 12k_Drive_End_Bearing_Fault_Data/         60 .mat files
├── models/                       written by Part II (the saved Keras model)
├── figures/                      written by the notebooks
└── results/                      written by the notebooks (CSV)
```

`scripts/cwru_data.py` is imported by **both** notebooks. That is deliberate: it guarantees
Part I and Part II are fitted and scored on exactly the same windows, so the comparison in
Task II.3 is between models rather than between pipelines. Part I writes its test predictions
to `results/part1_test_predictions.csv`, and Part II reloads them and asserts that the test
labels match before comparing. The 33 features are computed inside Part I itself (Task
I.2.5), where the assignment expects to see them.

---

## Running it

```bash
# 1. dependencies  (Python 3.11+)
pip install -r requirements.txt

# 2. the data  (~195 MB; needs git)
python scripts/download_data.py
python scripts/download_data.py --check     # verify: 4 + 60 .mat files

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
first. All paths are relative to the repository root; run from there.

**Runtimes** (4-core CPU, no GPU): Part I about **1.5 min** (45 s for the tasks, the rest for
the supplement). Part II about **15 min**, almost all of it network training: 14 trainings for
the seed-stability and capacity studies plus 11 in the supplement (label formats, validation
schemes, augmentation). No GPU is needed or used.

---

## Course-lab supplements

Each notebook ends its tasks and then carries one **supplement** (`#supplement`) that works
through every technique taught in the MOD550 labs on the bearing data, so each lecture idea
is shown on our own measurements rather than on wine, glass, oil spills, MNIST or CIFAR-10.
Same dataset, same windows, same split, same two model families. The SVM lab is in
`Part_I_SVM.ipynb` (sections A and B) and the CNN lab is in `Part_II_Deep_Learning.ipynb`
(section C).

**Why after the last task, not inside it.** Part I says the 3 hp test load is "still
untouched" (I.4) and "scored once" (I.5). Several lab demos print test-load numbers, so
putting them inside I.3 or I.4 would make those sentences false. Each supplement therefore
sits after its notebook's last task, reuses the objects the tasks built (`F`, `Xtr`, `pred`,
`leaky`, `honest`, ...) rather than rebuilding them, changes no number reported in the tasks,
and is outside the word-limited reports. The task cells above it are unchanged.

| Notebook | Section | Course source | Method |
|---|---|---|---|
| Part I | A1 | CNN lab slide 16 | always look at the data first |
| Part I | A2 | SVM lab 3-4, `svm_1_wine_duplicates.py` | scaling, the two scalers, fit on train only |
| Part I | A3 | `svm_3_Oil_spill.py` | the hidden trap: id-like and constant columns |
| Part I | A4 | SVM lab 19 | `stratify=y` is not optional |
| Part I | A5 to A7 | SVM lab 5-7, `svm_2_glass_gamma.py` | `kernel`, `C`, `gamma`, drawn on bearing features |
| Part I | A8 | SVM lab 8, `svm_3_Oil_spill.py` | `class_weight`, what a mistake costs |
| Part I | A9 | SVM lab 9 | choosing `C` and `gamma` without cheating |
| Part I | A10 to A13 | SVM lab 10-13 | confusion matrix, metrics by hand, macro average, `scoring=` |
| Part I | A14 | SVM lab 21 | the three tricks, on bearings |
| Part I | B | `Spatial_Analysis.pdf` | Tobler's law, semivariogram, correlogram, range |
| Part II | C1 | `01_mnist_cnn.py` | always look at the data first |
| Part II | C2 to C7 | CNN lab 3-10 and 20, `CNN-example.py` | dense vs conv, kernels, padding, parameters, pooling, network shape |
| Part II | C8 to C9 | CNN lab 13-15 | label formats, the training knobs |
| Part II | C10 | `02_mnist_confusion.py` | the worst-confusions ranking loop |
| Part II | C11 | `03_cifar_cnn.py` | augmentation and dropout |
| Part II | C12 to C13 | `01_mnist_cnn.py`, `05_predict_photo.py` | save/reload, and one brand new measurement |

Each supplement opens with its own table naming the task each section extends, and ends with
a "what each lab method said" summary, saved as `results/part1_method_summary.csv` and
`results/part2_method_summary.csv`.

**Four findings argue against lab habits. Only the first argues against a choice a task
made.** All four are reported rather than quietly fixed, so the tasks still describe what was
actually run:

1. **`class_weight="balanced"` is the wrong default here** (A8, a choice made in Task I.4). It
   costs about 0.06 macro-F1 (0.908 without it, 0.845 with it) and protects nothing: `Normal`
   recall is 1.000 either way, while `Ball_021` recall falls from 0.661 to 0.254. The rare
   class was never the problem, so weighting by frequency aims the correction at the wrong
   target. For that reason the CNN-lab models in Part II are trained without `class_weight`
   and are not interchangeable with Task II.3's.
2. **Fitting the scaler on all data gains 0.12 macro-F1** (A2). The tasks already fit the
   scaler inside a `Pipeline`, so this measures what the lab's shortcut would have cost, and
   the two scalers differ by only 2% in the median feature. A score that moves that far under
   a 2% preprocessing change should not be quoted to three decimals.
3. **`validation_split=0.1`, the idiom both lab scripts use, fails badly here** (C9). It
   takes the *last* 10% rather than a random 10%, and our windows are ordered by recording,
   so it holds back a single class and reports validation accuracy 0.000. Shuffled first it
   reports a flattering 0.687, because those windows share recordings with training. Task
   II.3 validates on a held-out motor load, which avoids the trap.
4. **`GridSearchCV(cv=5)` claims 0.999 and delivers 0.879** (A9). Leave-one-load-out also
   overstates (it claims 0.989 and delivers 0.845), but KFold's claim is the less believable,
   because it scores each fold on windows whose neighbours it has just trained on.

The variogram section (B) turns an assertion into a measurement. Three of four recordings
are effectively independent one window apart, but `OR_021 @6 o'clock` correlates 0.56 at lag
1 with a range of six windows, about a second of signal. A random split cannot know which
recordings behave which way, which is why splitting by recording is the only safe choice.

### Reproducibility

- `SEED = 42` throughout; `keras.utils.set_random_seed` is called inside `build_cnn` and
  `build_cnn_lab`.
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
| ... | *(your own contribution)* |

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
| Claude (Anthropic) | Dataset selection; `scripts/cwru_data.py`; feature-extraction code; all modelling and plotting code in both notebooks; the CNN architecture; `download_data.py`; the draft group-section commentary | Code kept and executed as written. **The group-section prose is a draft that must be read, checked and rewritten where you disagree with it.** |
| Claude (Anthropic) | The two **supplements** (lab methods applied to this data, one at the end of each notebook): code, figures and commentary, built from the course lab scripts and slides | Code kept and executed. Same rule: the commentary is a draft to be read and owned before submission. |
| Claude (Anthropic) | Diagnosing the `99_Normal_2.mat` duplicate-channel bug after the duplicate-window check flagged 59 duplicates | Fix kept; the regression check was retained in the notebook |
| n/a | **Individual Analysis sections (Part I Q1–3, Part II Q1–3)** | **Not AI-written. These are left as evidence summaries plus `*Write your answer here.*` placeholders and must be written by you.** |

---

## Submission checklist

Deadline: **23:59, Friday 20 November 2026**. In order:

- [ ] **1. Get it running.** `pip install -r requirements.txt`, then
      `python scripts/download_data.py`, then run `Part_I_SVM.ipynb` and
      `Part_II_Deep_Learning.ipynb` in that order, start to finish, from a clean kernel.
      Confirm Part I's duplicate check still reports **0**.
- [ ] **2. Read both notebooks end to end, supplements included.** You have to be able to
      explain any line you submit. Anything you cannot defend, change or delete. Each
      supplement is one contiguous block between the last task and the Individual Analysis,
      so if the group decides it does not want one, it can be removed without touching the
      graded tasks.
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
      II.1 ≤ 100, and each individual answer ≤ 300. The supplements are labelled in the
      notebooks as outside these reports.
- [ ] **7. Re-run both notebooks one last time** so the committed outputs match the
      committed code, and confirm cell numbering runs 1..n in order.
- [ ] **8. Push to your own GitHub repository**: one per student, containing both
      notebooks, this README, `requirements.txt` and `scripts/`. Confirm `data/` is **not**
      committed (it is in `.gitignore`; the assignment caps committed data at ~50 MB and
      this is 195 MB).
- [ ] **9. Clone your own repo somewhere fresh and run it** to prove the download script and
      relative paths work for someone who is not you.

---

## Citation

> Case Western Reserve University Bearing Data Center. *Seeded Fault Test Data*.
> <https://engineering.case.edu/bearingdatacenter> (accessed November 2026).
> Files obtained via the public mirror <https://github.com/s-whynot/CWRU-dataset>.

Further reading on this dataset's quirks, not relied on for any claim made above (the
anomalies in Task I.2 were found in the data itself, not taken from the literature):

> W. A. Smith and R. B. Randall, "Rolling element bearing diagnostics using the Case Western
> Reserve University data: A benchmark study," *Mechanical Systems and Signal Processing*,
> vol. 64–65, pp. 100–131, 2015. doi:10.1016/j.ymssp.2015.04.021
