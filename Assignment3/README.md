# MOD550 Assignment 3 - Bearing fault classification with SVM and CNN

We classified short windows of drive-end bearing vibration from the CWRU Bearing Data Center into four classes: **normal, inner-race fault, ball fault and outer-race fault**.

- **Part I** (`Part_I_SVM.ipynb`) compares linear and RBF support vector machines on eight engineered features, with logistic regression as the alternative classifier.
- **Part II** (`Part_II_CNN.ipynb`) trains a compact one-dimensional CNN on the raw 0.25-second windows.

Both parts use the same 40 recordings, the same 1,578 windows and the same split by motor load: training 0-1 HP, validation 2 HP, test 3 HP.

## Results at a glance

Test load 3 HP, 400 windows from 10 recordings.

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| Linear SVM (selected on validation) | 0.8900 | 0.7572 |
| RBF SVM | 0.9875 | 0.9854 |
| Logistic regression | 0.9950 | 0.9958 |
| 1-D CNN (selected epoch 31) | 0.8300 | 0.8519 |

The majority-class baseline scores a validation macro-F1 of 0.1154. Details and limitations are in the notebooks.

## Repository contents

| Path | What it is |
|---|---|
| `Part_I_SVM.ipynb` | Part I: Tasks I.1-I.5 |
| `Part_II_CNN.ipynb` | Part II: Tasks II.1-II.4 |
| `signal_preparation.py` | Shared signal preparation, imported by both notebooks; not run on its own. It resamples to 12 kHz, applies a 4.5 kHz low-pass filter and trims 0.05 s at each edge. |
| `refresh_part_i_images.py`, `refresh_part_ii_images.py` | Update the images embedded in the notebooks after a re-run (see step 5 below) |
| `requirements.txt` | Package versions |
| `data/` | CSV tables, the CNN input archive (`.npz`) and JSON run records, all written by the notebooks |
| `figures/` | Plots written by the notebooks |
| `figures_of_data/` | PNG pictures of the CSV tables |
| `public_dataset/` | Downloaded CWRU pages and `.mat` recordings. It is **not committed** (about 140 MB) and is recreated by Part I. |

## Dataset

**Source:** Case Western Reserve University, Bearing Data Center. *Bearing Data Center* [dataset]. https://engineering.case.edu/bearingdatacenter (accessed 15 November 2026).

The data are real laboratory measurements from a 2 hp motor test rig. Faults were seeded by electro-discharge machining in SKF 6205-2RS JEM drive-end bearings. The signal used is the drive-end acceleration.

We used 40 recordings: the four normal baselines and the 12 kHz drive-end fault recordings. Each class and fault size has one recording per motor load (0, 1, 2 and 3 HP).

| Class | Fault diameter (inch) | Official labels | File numbers | Sampling rate |
|---|---|---|---|---|
| Normal | - | Normal_0 to Normal_3 | 97, 98, 99, 100 | 48 kHz (resampled to 12 kHz) |
| Inner race | 0.007 / 0.014 / 0.021 | IR007, IR014, IR021 (_0 to _3) | 105-108, 169-172, 209-212 | 12 kHz |
| Ball | 0.007 / 0.014 / 0.021 | B007, B014, B021 (_0 to _3) | 118-121, 185-188, 222-225 | 12 kHz |
| Outer race, 6 o'clock | 0.007 / 0.014 / 0.021 | OR007@6, OR014@6, OR021@6 (_0 to _3) | 130-133, 197-200, 234-237 | 12 kHz |

**Download:** it is not needed to download anything by hand.

- Part I (code cell 1) finds each file by its official label in the CWRU tables and downloads it from `https://engineering.case.edu/sites/default/files/<number>.mat`.
- It stores every file's SHA-256 fingerprint in `public_dataset/acquisition_manifest.json` and checks the files against these fingerprints on later runs.
- The raw data (about 140 MB) are excluded by `.gitignore`, as the assignment asks for data over about 50 MB.

**Licence and usage:**

- The data are publicly downloadable from the original provider, which describes research use.
- No explicit dataset licence or general reuse permission was found on the provider's pages. The raw recordings are therefore not redistributed in this repository.
- Source notes are in [Sources for Task I.1](#sources-for-task-i1).

## Dependencies

Install with `python -m pip install -r requirements.txt`. The file pins:

- numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, matplotlib 3.11.2, scikit-learn 1.9.1, ipython 9.17.1, Pillow 12.3.0
- tensorflow 2.22.0rc0, keras-nightly 3.16.0.dev2026110403, h5py 3.15.1

The saved notebook outputs were produced in these environments:

| Notebook | Environment of the saved run |
|---|---|
| Part I | Windows, Python 3.14.7, numpy 2.5.3, pandas 3.0.6, scipy 1.18.1, matplotlib 3.11.2, scikit-learn 1.9.1 (verified rerun, 20 November 2026; shown in the output of code cell 1) |
| Part II | Python 3.14.7, numpy 2.5.3, scipy 1.18.1, TensorFlow 2.22.0rc0, Keras 3.16.0.dev2026110403 (`keras-nightly`), h5py 3.15.1 (stored in `data/II2_preparation_metadata.json`) |

Notes:

- The table pictures are drawn with the Windows font Consolas (`C:/Windows/Fonts/consola.ttf`), so the notebooks run as they are on Windows.
- Part II code cell 3 records the installed versions of the packages named `tensorflow` and `keras-nightly`, so these two packages must be installed under exactly these names.

## How to run

1. **Install** the packages listed above in the Python environment used by the notebook kernel.
2. **Open the project folder**, which is the folder that contains both notebooks. The folder can be opened using VS Code or Jupyter. The notebooks use this folder as their working folder, and if there is an issue with the folder location, the first code cell stops and explains how to fix it with `os.chdir(...)`.
3. **Run Part I:** open `Part_I_SVM.ipynb`, restart the kernel, then *Run All*. It takes about 30 seconds once the data are saved. The first run also downloads about 140 MB. It creates `data/`, `figures/` and `figures_of_data/` if they are missing.
4. **Run the image-refresh utility Part I:** save and close Part_I_SVM.ipynb. Run: python refresh_part_i_images.py. Reopen it to view the refreshed images.
5. **Run Part II:** open `Part_II_CNN.ipynb`, restart the kernel, then *Run All*. It takes about 3 minutes, mostly CNN training. Part II reads Part I's CSV files.
    - **On a new computer, always run Part I first.** Part II checks that its windows match the fingerprints Part I saved. Tiny numerical differences between computers in the 48-to-12 kHz resampling change the fingerprints of the 138 normal windows, so old CSV files from another computer make Part II stop.
6. **Run the image-refresh utility Part II:** save and close Part_II_CNN.ipynb. Run: python refresh_part_ii_images.py. Reopen it to view the refreshed images.


Notes:

- Steps 4 and 6 described above are precaution steps to ensure that the figures embedded in the notebooks are the latest ones. The scripts run in these steps only replace the embedded images. They do not run code or change results. The reason to take these precaution steps is because the figures (images) embedded in the notebooks are static copies of the PNG files from a previews execution; Running the code creates CSV files, figures and model results, but does not automatically update the embedded figures displayed in the notebooks. After execution, saving and closing each notebook, running its corresponding image-refresh utility, and reopening each notebook, ensures that the displayed figures reflect the latest results, whether running the notebooks for the first time or repeating the analysis.
- `signal_preparation.py` is used automatically by both notebooks when called. Keep it beside the notebooks; do not run it separately.
- In Part II, code cells 1-7 must run in one session. The CNN is kept in memory and no model file is saved, so after a kernel restart Part II must be run again from the top.
- Code cell 8 (Task II.4) only reads saved files and can be run on its own.
- Randomness: Part I contains no random steps; the split is fixed by load. Part II uses seed 550 and deterministic TensorFlow operations. On other hardware or package versions the losses can differ in the last decimals.
- Re-run check (19 November 2026): both notebooks were re-run from scratch on Linux with Python 3.13, TensorFlow 2.21 and Keras 3.15. Only the font paths and the version lookup in Part II code cell 3 were adjusted for that computer. All Part I results were identical (only the fingerprints of the 138 normal windows differed, as explained in step 4). The CNN again ran 46 epochs, selected epoch 31 and gave the same test predictions and metrics.

## References

The notebooks cite these sources by the labels below.

### Sources for Task I.1

- [1] CWRU Bearing Data Center. [Welcome / overview](https://engineering.case.edu/bearingdatacenter/welcome).
- [2] CWRU Bearing Data Center. [Apparatus and Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures).
- [3] CWRU Bearing Data Center. [12k Drive End Bearing Fault Data](https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data).
- [4] CWRU Bearing Data Center. [Normal Baseline Data](https://engineering.case.edu/bearingdatacenter/normal-baseline-data) and [Fault Specifications](https://engineering.case.edu/bearingdatacenter/fault-specifications).
- [5] CWRU Bearing Data Center. [Project History](https://engineering.case.edu/bearingdatacenter/project-history). It describes research use; this is not a licence.

Also consulted for the licence search:

- [Download a Data File](https://engineering.case.edu/bearingdatacenter/download-data-file)
- [Bearing Information](https://engineering.case.edu/bearingdatacenter/bearing-information)
- [CWRU Faculty Handbook 2025-2026](https://case.edu/facultysenate/sites/default/files/2026-01/Faculty%20Handbook%202025-2026.pdf)
- [Scholarly Commons policies](https://commons.case.edu/facultyworks/policies.html)

None of these grants a dataset licence.

### Sources for Task I.2

- [I.2-1] CWRU Bearing Data Center. [Normal Baseline Data](https://engineering.case.edu/bearingdatacenter/normal-baseline-data), [12k Drive End Bearing Fault Data](https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data) and [Apparatus and Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures). Accessed 15 November 2026.
- [I.2-2] Smith, W. A., and Randall, R. B. (2015). Rolling element bearing diagnostics using the Case Western Reserve University data: A benchmark study. *Mechanical Systems and Signal Processing*, 64-65, 100-131. https://doi.org/10.1016/j.ymssp.2015.04.021. Used for the sampling rates (Tables A1-A2) and the possible clipping in 236 and 237 (Table 3).
- [I.2-3] SciPy. [resample_poly](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html).
- [I.2-4] SciPy. [sosfiltfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html).
- [I.2-5] SciPy. [kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html).
- [I.2-6] Hendriks, J., Dumond, P., and Knox, D. A. (2022). Towards better benchmarking using the CWRU bearing fault dataset. *Mechanical Systems and Signal Processing*, 169, 108732. https://doi.org/10.1016/j.ymssp.2021.108732.

### Sources for Task I.4

- [I.4-1] scikit-learn. [SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html).
- [I.4-2] scikit-learn. [PredefinedSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.PredefinedSplit.html) and [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html).
- [I.4-3] scikit-learn. [RBF SVM parameters](https://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html).

### Sources for Task II.1

- [II.1-1] Keras. [Conv1D layer](https://keras.io/api/layers/convolution_layers/convolution1d/).

### Sources for Task II.2

- [II.2-1] Keras. [The Sequential model](https://keras.io/guides/sequential_model/).
- [II.2-2] Keras. [Conv1D layer](https://keras.io/api/layers/convolution_layers/convolution1d/).
- [II.2-3] Keras. [MaxPooling1D](https://keras.io/api/layers/pooling_layers/max_pooling1d/) and [GlobalAveragePooling1D](https://keras.io/api/layers/pooling_layers/global_average_pooling1d/).
- [II.2-4] Keras. [Probabilistic losses](https://keras.io/api/losses/probabilistic_losses/) (SparseCategoricalCrossentropy).

### Sources for Task II.3

- [II.3-1] Keras. [Adam](https://keras.io/api/optimizers/adam/).
- [II.3-2] Keras. [Probabilistic losses](https://keras.io/api/losses/probabilistic_losses/) and [model training APIs](https://keras.io/api/models/model_training_apis/).
- [II.3-3] Keras. [Writing your own callbacks](https://keras.io/guides/writing_your_own_callbacks/) and [EarlyStopping](https://keras.io/api/callbacks/early_stopping/).

### Sources for Task II.4

- [II.4-1] CWRU Bearing Data Center. [Apparatus and Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures). Load and speed; effect of the outer-race position relative to the load zone.
- [II.4-2] CWRU Bearing Data Center. [12k Drive End Bearing Fault Data](https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data). Accessed 18 November 2026.

## AI log

AI tools were used for code, debugging, figures and documentation, as allowed by the assignment. Every result was checked by running the notebooks.

| Date (2026) | Tool | What we used it for | What we kept / changed |
|---|---|---|---|
| 15 Nov | ChatGPT/Codex (web search, Python) | Task I.1: check the original CWRU sources and licence status, select the recordings, draft the problem statement | Kept the four-class problem, the 40-recording selection (shared fault sizes, outer race at 6 o'clock) and the licence finding. Moved the data download to I.2 and the source notes to this README. |
| 15 Nov | ChatGPT/Codex (Python, Node.js, web) | Task I.2: download and audit the recordings, eight features, five figures, CSV tables | Kept the audit, features and figures. Changed: channel chosen by file ID (the duplicate in 99.mat), documented missing RPM, resampling and clipping, scaler left unfitted until I.3, duplicate outputs removed. |
| 15 Nov | ChatGPT/Codex (Python, documentation) | Task I.3: load-based split, leakage checks, macro-F1, majority baseline | Kept as implemented; added the split inventory and checks. |
| 16 Nov | ChatGPT/Codex (Python, documentation) | Tasks I.4-I.5: SVM tuning (56 settings), logistic regression, test evaluation, figures and discussion | Kept the linear SVM after the validation tie; the test set was scored once with no retuning. Clarified the balanced class weights. |
| 16-19 Nov | ChatGPT/Codex (PDF rendering) | PDF exports of both reports | Layout only; notebook content unchanged. |
| 17 Nov | Claude (Anthropic) | Review of the Part I draft: found the `figures_of_data` error and the Windows-only font paths, and suggested fixes | [check] Automatic folder creation and rendering of all I.2/I.3 tables were then implemented (19 Nov). |
| 18 Nov | ChatGPT/Codex (Python, TensorFlow/Keras, documentation) | Tasks II.1-II.2: dataset reuse, CNN choice, shared `signal_preparation.py`, input tensors, 4,004-parameter CNN | Kept the same windows and split; verified 40 file and 1,578 window fingerprints. |
| 18 Nov | ChatGPT/Codex (Python, TensorFlow/Keras) | Tasks II.3-II.4: training protocol, learning curves, test evaluation, error analysis (Option B) | Kept one seeded run, epoch 31 selected on validation, test scored once; error analysis without retraining. |
| 19 Nov | ChatGPT/Codex (Python) | Re-run fixes: create output folders, render all table images, image-refresh scripts, keep the CNN in memory (no model files), run instructions | Kept all analysis and results; a clean rebuild gave the same results. |
| 19 Nov | Claude (Anthropic) | Shortened this README; wrote an explanation of every code cell for our own understanding; made a guide with evidence and points (no answer text) for the individual questions; test re-run of both notebooks | [fill in what you kept or changed] |

## Group contributions

| Member | Contributions |
|---|---|
| Claudio Alberto Lucas De Oliveira | Part I code and analysis, Part II implementation, notebook review and test run, README |
| Uliana Kulebyakina | Part II code and analysis, Part I implementation, notebook review and test run, README |