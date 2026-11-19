# Assignment 3 development

## Folder conventions

- `public_dataset/`: all original downloads and accompanying source materials; preserve raw recordings unchanged.
- `figures/`: PNG outputs produced by our code only.
- `data/`: derived CSV tables, prepared NPZ tensors and JSON provenance produced by our code only.
- `figures_of_data/`: readable PNG tables generated from the derived CSV files.
- `models/`: saved model archives with explicit initial/trained status.
- Notebook and documentation: directly within mother folder.

## Execution Instructions

### Execution sequence

Follow this sequence for a complete rebuild, using `draft-A` as the working directory:

```text
1. Select the intended Python environment and notebook kernel.
   If required, install dependencies: python -m pip install -r requirements.txt
2. Open Part_I_SVM.ipynb, restart its kernel and run all cells in notebook order.
3. Save and close Part_I_SVM.ipynb.
   Run: python refresh_part_i_images.py
   Reopen it to view the refreshed images.
4. Open Part_II_CNN.ipynb, restart its kernel and run all cells in notebook order.
5. Save and close Part_II_CNN.ipynb.
   Run: python refresh_part_ii_images.py
   Reopen it to view the refreshed images.
6. Regenerate the PDF reports separately when their displayed content changes.
```

### Considerations and exceptions

#### Environment and retained source files

Keep both notebooks beside `signal_preparation.py`, `requirements.txt`, `refresh_part_i_images.py` and `refresh_part_ii_images.py`. The Part II utility reuses the attachment-refresh function in the Part I utility, so keep both files together. No separate image-rebuilding script is required.

The recorded execution environment is Python 3.14.7, TensorFlow 2.22.0-rc0, Keras 3.16.0.dev2026110403 (the `keras-nightly` distribution) and h5py 3.15.1; other package versions are in `requirements.txt`. These include prerelease framework versions. Matching the seed does not guarantee bitwise-identical results across framework versions or hardware.

Preserve `public_dataset`, including cached source pages, original MAT recordings and the acquisition manifest. Part I reuses cached files after checksum verification. If the cache is missing, acquisition requires access to the original CWRU URLs. Raw downloads total approximately 140 MB and are excluded from version control.

#### Setting the notebook kernel’s working directory

Set the notebook kernel’s working directory to the folder containing both notebooks and the supporting project files (for instance, working directory "draft_A").

To set it, run the following in a notebook cell before running the project code, replacing the example path with your actual folder:

```python
import os
os.chdir(r"C:\path\to\draft_A")
```

Confirm the location with:

```python
from pathlib import Path
print(Path.cwd())
```

"draft_A" is only an example folder name. The current project folder is `C:\Users\claud\Assignment-3-GroupSHARED\Assignment-3\drafts\draft-A`; use that path while the project remains there. Setting the directory applies to the current kernel session. After restarting the kernel, check the directory again and repeat the command if needed. The notebook checks report these instructions when the expected notebook file is absent from the working directory; they do not change the directory automatically.

#### Moving the notebooks to another folder

For a straightforward move of the two notebook files to a new folder, keep these together:

- `signal_preparation.py`.
- Both refresh utilities (two Python files): `refresh_part_i_images.py` and `refresh_part_ii_images.py`.
- `requirements.txt`, so the required package versions remain documented.

The required Python packages must also be installed in the environment used by the notebook kernel; they are not files to copy into the project folder. If necessary, install them using `python -m pip install -r requirements.txt`.

Subfolders and their contents are recreated by running Part I fully, followed by Part II. Internet access to the original CWRU source is required to download original data if `public_dataset` is not moved with the notebooks. Move existing subfolders too if you want to retain their recordings, results, models and images instead of rebuilding them.

The refresh utilities locate their notebooks relative to the scripts’ own location, so they remain portable when moved together. Notebook filenames must remain unchanged.

The destination folder does not need to be named `draft-A`. Set the notebook kernel’s working directory to that destination folder: both notebooks resolve project paths using `Path.cwd()`. See the working-directory instructions above.

#### When a full run is required

Running Part I first supplies the required folders and inventories. If all CSVs are deleted, Part I must run before Part II because Part II reuses Part I’s data inventories. Part I creates `data`, `figures` and `figures_of_data` automatically, including when those directories were removed. It recreates 17 CSVs, 17 table PNGs and eight plot PNGs, and repeats its model selection and evaluation. The ten I.2/I.3 table images are rendered immediately after their CSVs are written; I.4/I.5 retain their existing rendering steps.

If Part II’s CSVs are deleted, run Part II fully to recreate its CSVs, figures and CNN training (and evaluation) results. If Part I’s required inventories and folders still exist, Part I need not be repeated solely because Part II’s CSVs were deleted. The full Part II run verifies inventories in II.1, reconstructs inputs and saves the initial model in II.2, trains/selects/evaluates the CNN in II.3 and analyses its saved predictions in II.4. Its model-output step creates `models`. A full run rewrites the corresponding generated artifacts; neither attachment-refresh command performs training or evaluation.

To reproduce only II.4 from retained results, its standalone code cell 8 can run from `draft-A` without rerunning earlier cells. It requires `data/II3_test_predictions.csv`, `data/II3_class_metrics.csv`, `data/II3_run_metadata.json`, `data/II2_input_inventory.csv`, `data/I2_recording_inventory.csv` and `models/II3_selected_model.keras`, plus the output folders. This analyses fixed predictions without additional inference.

#### Why embedded images need refreshing

External PNG files and embedded markdown attachments are separate copies. Running notebook code regenerates files on disk but does not automatically replace saved markdown attachments. The refresh commands update 18 Part I images and 12 Part II images from their respective external PNGs. Each image cell records its source directory in metadata, disambiguating table and plot PNGs with the same filename.

Save and close the relevant notebook before refreshing, then reopen it. This prevents an editor from overwriting refreshed attachments with older copies. The shared refresh function reads all required images before writing; a missing image leaves the notebook unchanged. It preserves code, saved execution outputs and numerical results.

#### PDF exports

PDFs are separate exports. Running notebook cells or refreshing markdown attachments does not update them. Regenerate the relevant PDF after changes to displayed notebook content, then check figures, tables and notebook cell references.

## Task I.1 - Engineering Problem and Dataset

### Source notes

All URLs below were reviewed and these are research notes only, not copies of the source pages.

| Source | URL | Evidence and use |
|---|---|---|
| CWRU Bearing Data Center overview | https://engineering.case.edu/bearingdatacenter/welcome | Normal and deliberately faulted motor bearings; experiments use a 2 hp motor. Faults were introduced by electro-discharge machining. |
| Apparatus and Procedures | https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures | Motor, torque transducer/encoder, dynamometer; housing-mounted accelerometers; 12 kHz and 48 kHz acquisition. SKF bearings for 0.007, 0.014, and 0.021 inch defects. |
| Download a Data File | https://engineering.case.edu/bearingdatacenter/download-data-file | MATLAB recordings; DE, FE, BA and RPM naming conventions. Individual channel availability still needs checking. |
| Normal Baseline Data | https://engineering.case.edu/bearingdatacenter/normal-baseline-data | Four normal recordings, loads 0-3 HP, approximate speeds 1797, 1772, 1750 and 1730 rpm. This table does not explicitly state baseline sampling rates. |
| 12k Drive End Bearing Fault Data | https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data | Fault-recording labels and experimental conditions. Three shared defect sizes permit comparable IR, ball and OR conditions. |
| Fault Specifications | https://engineering.case.edu/bearingdatacenter/fault-specifications | For selected drive-end faults, diameters 0.007, 0.014 and 0.021 inches and depths 0.011 inches; SKF manufacturer. |
| Bearing Information | https://engineering.case.edu/bearingdatacenter/bearing-information | Drive-end 6205-2RS JEM SKF bearing and documented defect-frequency multipliers; useful for later physically motivated features. |
| Project History | https://engineering.case.edu/bearingdatacenter/project-history | Provider describes the database as supporting validation and improvement of motor condition assessment techniques. This supports intended research context, not an explicit license. |
| 48k drive-end table | https://engineering.case.edu/bearingdatacenter/48k-drive-end-bearing-fault-data | Alternative acquisition group; outside the study scope. |
| Institutional Faculty Handbook 2025-2026 | https://case.edu/facultysenate/sites/default/files/2026-01/Faculty%20Handbook%202025-2026.pdf | Institutional search result discusses copyright, fair use assessment, and permissions generally. It does not grant rights to the bearing dataset. |
| Scholarly Commons policies | https://commons.case.edu/facultyworks/policies.html | Institutional repository permissions apply to that repository's submissions; they are not a dataset license for the Bearing Data Center. |

The apparatus prose and fault-table headings give inconsistent descriptions of the load zone relative to outer-race clock position. The study specifies the outer-race position as 6 o'clock without assigning a load-zone orientation.

### Engineering question and study scope

Can numerical descriptors of drive-end bearing vibration distinguish normal operation, inner-race faults, ball faults, and outer-race faults within documented laboratory conditions?

The study covers normal baselines and 12 kHz drive-end fault experiments at 0.007, 0.014 and 0.021 inch defect diameters, loads 0-3 HP, and outer-race position 6 o'clock. This gives 40 candidate recordings: 4 normal and 12 per fault class. Restricting outer-race position reduces one source of variation. Choosing shared sizes avoids the missing outer-race cases and manufacturer change associated with 0.028 inch defects.

Drive-end (DE) vibration is the signal input. Bearing condition is the target. Fault diameter, load, RPM, position, and original recording identity are metadata initially. Task I.2 defines window length, features, filtering and any resampling, and verifies file- and channel-specific sampling rates before combining recordings.

Evaluation must keep related windows from the same recording within one partition and account for shared specimens and operating conditions. Recording counts differ between classes, and window counts depend on recording durations. Seeded laboratory faults do not establish early-fault detection, remaining useful life prediction, or field deployment performance.

### Recording inventory

Inventory of candidate recordings identified in the official tables. Each row covers four labels in load order 0, 1, 2, 3 HP, with approximate speeds of 1797, 1772, 1750, 1730 rpm, respectively. Task I.2 verifies which recordings meet the study requirements.

| Condition | Diameter inches | OR position | Official recording labels | Source table |
|---|---|---|---|---|
| Normal | Not applicable | Not applicable | Normal_0, Normal_1, Normal_2, Normal_3 | Normal Baseline Data |
| Inner race | 0.007 | Not applicable | IR007_0, IR007_1, IR007_2, IR007_3 | 12k drive end |
| Ball | 0.007 | Not applicable | B007_0, B007_1, B007_2, B007_3 | 12k drive end |
| Outer race | 0.007 | 6 o'clock | OR007@6_0, OR007@6_1, OR007@6_2, OR007@6_3 | 12k drive end |
| Inner race | 0.014 | Not applicable | IR014_0, IR014_1, IR014_2, IR014_3 | 12k drive end |
| Ball | 0.014 | Not applicable | B014_0, B014_1, B014_2, B014_3 | 12k drive end |
| Outer race | 0.014 | 6 o'clock | OR014@6_0, OR014@6_1, OR014@6_2, OR014@6_3 | 12k drive end |
| Inner race | 0.021 | Not applicable | IR021_0, IR021_1, IR021_2, IR021_3 | 12k drive end |
| Ball | 0.021 | Not applicable | B021_0, B021_1, B021_2, B021_3 | 12k drive end |
| Outer race | 0.021 | 6 o'clock | OR021@6_0, OR021@6_1, OR021@6_2, OR021@6_3 | 12k drive end |

### Citation and usage permissions

Dataset citation: Case Western Reserve University, Bearing Data Center. *Bearing Data Center* [dataset]. https://engineering.case.edu/bearingdatacenter (accessed 15 November 2026). The inspected pages do not specify a publication date or mandatory citation format.

Findings: data are publicly downloadable from the original provider. No explicit dataset license or blanket reuse permission was located in the inspected provider pages or the broader institutional search. The project-history page describes research applications, but this is not equivalent to a Creative Commons license, public-domain dedication, or unrestricted redistribution permission. General institutional copyright policies do not resolve the dataset-specific question. A license attached to a paper or third-party downloader cannot be assigned to these recordings.

### Sources for Task I.1

[1] [CWRU overview](https://engineering.case.edu/bearingdatacenter/welcome).

[2] [Apparatus and Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures).

[3] [12k Drive End Bearing Fault Data](https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data).

[4] [Normal Baseline Data](https://engineering.case.edu/bearingdatacenter/normal-baseline-data) and [Fault Specifications](https://engineering.case.edu/bearingdatacenter/fault-specifications).

[5] [Project History](https://engineering.case.edu/bearingdatacenter/project-history).

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-15 | ChatGPT/Codex | Analyse Task I.1 independently; reuse only the source URL; assess the retained Original proposal. | Four-requirement structure, four-class problem, original-source research, statement under 350 words. | Working location clarified to drafts/draft-A; source imports separated from generated PNG/CSV outputs. |
| 2026-11-15 | ChatGPT/Codex with web retrieval and local Python | Implement the agreed Task I.1 plan; broaden permissions research; maintain source notes, inventory and this log; draft analysis for later review. | Task I.1 notebook text, permissions findings, recording selection rationale and inventory. | Study restricted to shared SKF defect sizes and one OR position; feature and compatibility decisions reserved for Task I.2. |
| 2026-11-15 | ChatGPT/Codex with local Python | Keep Task I.1 concise and defer recording acquisition to Task I.2. | Problem statement, source notes, recording inventory and permissions findings. | Removed acquisition script, download-status commentary and acquisition instructions. |
| 2026-11-15 | ChatGPT/Codex with local Python | Present notebook and Readme content as final answers; reserve candidate for recordings awaiting verification. | Study choices, source evidence, permissions findings and user edits. | Removed proposal framing, clarified study scope and consolidated the log table. |
| 2026-11-15 | ChatGPT/Codex with local Python | Organise Readme by task and move notebook sources into the corresponding task section. | Statement, numbered references and existing edits. | Grouped supporting sections under Task I.1 and moved its source list to Readme. |


## Task I.2 - Data Exploration and Preparation

### Source notes

| Source | Evidence used |
|---|---|
| Original CWRU recording tables and MAT files [I.2-1] | Forty recording links resolved directly from official labels. Original files are preserved under `public_dataset/recordings/`, with eight accompanying pages under `public_dataset/source_pages/`. SHA-256 checks and URLs are retained in the acquisition manifest and generated inventory. |
| Smith and Randall (2015), Tables A1-A2 and Table 3 [I.2-2] | Normal baseline DE rate 48 kHz; selected fault DE rate 12 kHz; possible clipping in 236DE and 237DE. Rates are documentary metadata, not measurements inferred from array length. |
| SciPy documentation [I.2-3 to I.2-5] | Polyphase resampling with anti-alias filtering, forward-backward filtering, and Pearson kurtosis convention. |
| Hendriks et al. (2022) [I.2-6] | Bearings were reused across operating conditions; different recordings do not necessarily represent independent specimens. |
| scikit-learn documentation [I.2-7] | StandardScaler estimates feature means and standard deviations from training data. |

### Recording inventory

All 40 recordings meet the structural requirements and are retained. The code selects the variable matching the file ID. Extra `X098_DE_time` and `X098_FE_time` arrays in `99.mat` duplicate recording 98 and are not selected. RPM is absent from 98 and 99. Records 236 and 237 retain documented peak truncation (clipping) flags. Detailed file dimensions, original URLs, hashes, channel types and quality checks are in `data/I2_recording_inventory.csv` and `data/I2_channel_inventory.csv`.

| Class | Recordings | Original DE rate | Original samples per recording | Prepared windows |
|---|---:|---:|---:|---:|
| Normal | 4 | 48 kHz | 243,938-485,643 | 138 |
| Inner race | 12 | 12 kHz | 121,265-122,917 | 480 |
| Ball | 12 | 12 kHz | 121,410-122,571 | 480 |
| Outer race | 12 | 12 kHz | 121,410-122,571 | 480 |

### Preparation and outputs

Signal preparation is imported from `signal_preparation.py`, stored alongside both notebooks. Parts I and II use the same function for resampling, filtering and edge trimming. All 1,578 reconstructed windows match Part I's saved hashes, confirming unchanged preparation results.

The notebook resamples normal DE signals to 12 kHz, applies a common 4.5 kHz low-pass filter, trims 0.05 s at each edge, and extracts disjoint 0.25 s windows. Incomplete tails are discarded and counted. Windows are mean-centred; amplitude is retained. Eight predictors describe amplitude, impulsiveness and spectral content. No missing-predictor imputation, statistical outlier removal or oversampling is required by the audit. Possible peak truncation (clipping) remains a measurement limitation rather than being silently repaired.

The resulting feature matrix has 1,578 rows and eight float64 predictors. Missing RPM and normal fault diameter are metadata missingness, not missing model inputs. No selected signals, prepared windows or feature vectors are exact duplicates. Class imbalance is 138 normal windows versus 480 per fault class. Recording medians and full-window distributions are both displayed to avoid presenting windows as independent specimens.

| Output | Contents |
|---|---|
| `data/I2_recording_inventory.csv` | One row per original file: source, checksum, selected signal, dimensions, rates and quality metadata |
| `data/I2_channel_inventory.csv` | All numeric variable names, shapes, types, missingness and exact embedded duplicates |
| `data/I2_dataset_summary.csv` | Three dataset checks displayed in `figures_of_data/I2_dataset_summary.png` |
| `data/I2_processing_summary.csv` | Prepared sample counts, edge margins, window counts and discarded tails |
| `data/I2_window_features.csv` | Unscaled predictors, target and provenance/quality metadata; only the eight named FEATURES columns are model inputs |
| `data/I2_class_distribution.csv` | Class counts at recording and window levels |
| `data/I2_feature_audit.csv` | Feature types, ranges, missingness and descriptive three-IQR flags |
| `data/I2_feature_summary.csv` | Feature minima, medians and maxima by class |
| `data/I2_feature_correlations.csv` | Spearman feature correlations |
| `figures/I2_*.png` | Five figures: class counts, waveforms/spectra, feature distributions, correlations and anomaly diagnostics |

Scaling is defined as an unfitted pipeline and will be fitted only within training partitions in Task I.3. No classifier or data partition is created here. Class distributions and feature relationships are descriptive findings for this dataset, not estimates of predictive performance. The original sensor calibration range is not documented in the retained material, so plots use source acceleration units and no unsupported physical amplitude threshold is imposed. The raw-amplitude screen at 6.65 is descriptive only.

### Execution

See [Execution Instructions](#execution-instructions) for setup, notebook order and image refresh.

### Sources for Task I.2

[I.2-1] Case Western Reserve University, Bearing Data Center. [Normal Baseline Data](https://engineering.case.edu/bearingdatacenter/normal-baseline-data), [12k Drive End Bearing Fault Data](https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data), and [Apparatus and Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures). Accessed 15 November 2026.

[I.2-2] Smith, W. A., and Randall, R. B. (2015). Rolling element bearing diagnostics using the Case Western Reserve University data: A benchmark study. *Mechanical Systems and Signal Processing*, 64-65, 100-131. [DOI](https://doi.org/10.1016/j.ymssp.2015.04.021). Tables A1-A2 and Table 3 inspected in the [author-uploaded full text](https://www.researchgate.net/publication/276248554_Rolling_Element_Bearing_Diagnostics_Using_the_Case_Western_Reserve_University_Data_A_Benchmark_Study).

[I.2-3] SciPy. [resample_poly](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html).

[I.2-4] SciPy. [sosfiltfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html).

[I.2-5] SciPy. [kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html).

[I.2-6] Hendriks, J., Dumond, P., and Knox, D. A. (2022). Towards better benchmarking using the CWRU bearing fault dataset. *Mechanical Systems and Signal Processing*, 169, 108732. [DOI](https://doi.org/10.1016/j.ymssp.2021.108732).

[I.2-7] scikit-learn. [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html).

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-15 | ChatGPT/Codex with web retrieval, Node.js and Python | Develop Task I.2 independently using original-source downloads; provide diagnostic figures, preprocessing code, concise observations and clear docstrings. | Recording/channel audit, eight-feature extraction, five figures, generated CSV tables and reproducible notebook outputs. | Selected ID-matched variables to avoid embedded duplicates; documented missing RPM, baseline resampling and clipping flags; kept scaling unfitted until evaluation partitions are established. |
| 2026-11-15 | ChatGPT/Codex with Python | Place figures and selected tables in context without duplicate displays; add explanations in separate preceding text cells. | Existing numerical results and I.1/I.3 content. | Embedded five figures and six full table images once; replaced overlapping outputs and added concise interpretations before image cells. |
| 2026-11-15 | ChatGPT/Codex with Python | Suppress only output tables already represented in embedded PNG tables. | Calculations, CSV exports and outputs containing additional information. | Removed the duplicated recording-anomaly subset display and its saved output; retained software versions, channel-duplicate evidence, the feature preview and the partition summary. |
| 2026-11-15 | ChatGPT/Codex with Python | Replace the three printed dataset checks with a CSV-backed PNG and explain both it and the first-five-observation preview. | Existing dataset values, calculations and feature preview. | Added the summary CSV/PNG and preceding text cells; replaced the printed stream and moved the preview into its own display cell. |
| 2026-11-15 | ChatGPT/Codex with Python | Use peak truncation (clipping) in narrative and explain the anomaly figure in its preceding text cell. | Original source wording, compact table fields and diagnostic data. | Removed the figure supertitle, clarified both panel types and updated its embedded image. |
| 2026-11-18 | ChatGPT/Codex with Python | Explain the shared signal-preparation import in the Part I notebook and Readme. | Existing preparation code, data, figures and results. | Added a note before code cell 3 and in the Part I.2 preparation section; documented the shared local module and 1,578 matching window hashes. |

## Task I.3 - Classification Strategy and Baseline

### Split strategy and verification

Motor load determines membership; all windows from a recording stay together. The assignment is deterministic and needs no random seed. `data/I3_split_inventory.csv` retains each window's recording ID, class, load, index, content hash, condition/size grouping proxy and partition. The notebook verifies complete assignment, all-class and fault-size coverage, and no shared recording IDs or identical window hashes between partitions.

| Partition | Loads HP | Recordings | Normal windows | Inner-race windows | Ball windows | Outer-race windows | Total windows |
|---|---|---:|---:|---:|---:|---:|---:|
| Training | 0, 1 | 20 | 58 | 240 | 240 | 240 | 778 |
| Validation | 2 | 10 | 40 | 120 | 120 | 120 | 400 |
| Test | 3 | 10 | 40 | 120 | 120 | 120 | 400 |

This design evaluates cross-load transfer. Bearing specimens or installations can be shared across load conditions [I.3-1]; recording separation does not establish independence at the specimen level. The condition/size proxy is intentionally shared across partitions and is not evidence of unseen-bearing evaluation. Task I.2's full-dataset exploration also means the test is not completely blind. Test labels are not used for subsequent tuning or model selection. No test predictions or scores are computed in this task.

Only the eight Task I.2 FEATURES columns enter models. Identifiers, acquisition/load information, fault size and quality flags remain metadata. Scaling and any learned preprocessing must be fitted on training data only; any training cross-validation must refit them within each fold and preserve recording groups. The majority baseline does not require scaling because it ignores feature values.

### Primary metric and baseline

Macro-F1 is the sole tuning and selection metric [I.3-2]. It averages the four class F1 scores equally, so the normal minority class contributes as much as each fault class. The scoring function explicitly includes all four labels and sets undefined class F1 to zero.

The baseline predicts the most frequent training class [I.3-3]. Inner-race, ball and outer-race classes tie at 240 training windows each; the classifier resolves this deterministically to the alphabetically first label, `ball`. Validation macro-F1 is **0.1154**. No model or preprocessing setting was selected using test performance.

### Sources for Task I.3

[I.3-1] Hendriks, J., Dumond, P., and Knox, D. A. (2022). *Towards better benchmarking using the CWRU bearing fault dataset*. See the full reference [I.2-6] above for the shared-bearing limitation.

[I.3-2] scikit-learn. [f1_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html). Macro averaging and undefined-score handling.

[I.3-3] scikit-learn. [DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html). Training-majority baseline.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-15 | ChatGPT/Codex with Python and official documentation | Implement the agreed Task I.3 split, leakage controls, primary metric and baseline; keep the report within 200 words. | Fixed load-based partitions, macro-F1, training-majority baseline and shared-bearing/full-dataset-exploration limitations. | Added reproducible partition checks and a split inventory; fitted the reference classifier on training data and scored validation only. |

## Task I.4 - SVM Modeling

### Method and results

The notebook compares StandardScaler–SVC pipelines with linear and RBF kernels. The eight I.2 predictors and I.3 load partitions are unchanged. Class weights are fixed to `balanced` for both kernels and calculated from training labels only. The corresponding weights are 3.3534 for normal and 0.8104 for each fault class. Metadata never enter the model.

`PredefinedSplit` assigns all 778 training observations to fitting and all 400 validation observations to scoring. `GridSearchCV(refit=False)` prevents automatic refitting on the combined development set. Selected models are fitted on training only; assertions verify the scaler's training mean/variance and reproduce the search scores. No test predictions or scores are computed.

C = {0.001, 0.01, 0.1, 1, 10, 100, 1000}; RBF gamma = {0.0001, 0.001, 0.01, 0.1, 1, 10, 100}. All 56 configurations completed. One boundary extension would be allowed if the winning edge strictly improved on its adjacent profile value; neither kernel required it. Macro-F1 is the sole selection score. Numerical ties within 1e-12 prefer lower C, then lower gamma; a kernel tie prefers linear.

Selected linear: C = 1, training macro-F1 0.998958, validation 1.000000, 63 support vectors. Selected RBF: C = 1, gamma = 0.1, training 0.998958, validation 1.000000, 139 support vectors. The majority validation score remains 0.115385. Linear is retained because RBF adds no validation benefit. The single validation load, shared specimens and prior full-dataset exploration limit interpretation; perfect validation is not evidence of unseen-bearing generalisation.

### Generated outputs

- `data/I4_tuning_results.csv`: all 56 configurations, training/validation scores, gaps and selected flags.
- `data/I4_model_comparison.csv`: selected kernels and majority baseline; support-vector counts apply to SVMs only.
- `figures_of_data/I4_tuning_results.png` and `I4_model_comparison.png`: complete CSV-backed tables, with scores rounded to four decimals for display.
- `figures/I4_rbf_validation_heatmap.png` and `I4_regularisation_curves.png`: validation sensitivity and training/validation diagnostics.

The notebook embeds the comparison table and both diagnostic figures, with preceding text explanations. The complete search table is retained separately to avoid repeating the heatmap. Its Task I.4 prose is 287 words, including headings and explanations, below the 300-word limit. Existing I.1–I.3 cells are unchanged. The PDF now includes Tasks I.1–I.5.

### Sources for Task I.4

[I.4-1] scikit-learn. [SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html). C, kernels and balanced class weights. Accessed 16 November 2026.

[I.4-2] scikit-learn. [PredefinedSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.PredefinedSplit.html) and [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html). Fixed validation membership, training scores and refit control.

[I.4-3] scikit-learn. [RBF SVM parameters](https://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html). C/gamma interpretation and logarithmic search.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-16 | ChatGPT/Codex with Python and official documentation | Implement Task I.4 using the established split, concise documented code, CSV-backed tables and explained figures; keep discussion within 300 words. | Eight predictors, fixed load partitions, macro-F1 and original-source dataset. | Added 56-configuration linear/RBF tuning, training-only scaling and balanced weights, model comparison, diagnostic figures and final discussion; retained linear after a validation tie. |

| 2026-11-16 | ChatGPT/Codex with Python | Clarify the fixed balanced class-weight setting in the I.4 notebook. | Existing models, code and results. | Expanded the explanation of training-frequency weights, their numerical values and equal total class weight; verified the 300-word limit. |


## Task I.5 - Model Evaluation and Comparison

### Method and selection chronology

The eight features, fixed load partitions and preprocessing are unchanged. Both SVM configurations are retained from I.4. Balanced multinomial logistic regression provides a linear alternative with a different training objective; L2 regularisation uses `l1_ratio=0`, solver `lbfgs`, tolerance 1e-6 and at most 5000 iterations. Convergence warnings are treated as errors.

Logistic regression C was searched over {0.001, 0.01, 0.1, 1, 10, 100, 1000} using the same PredefinedSplit, training-only scaling and macro-F1 selection. No automatic refit on validation was allowed. C = 1 was selected: validation macro-F1 0.997917, tied with larger C values and preferred by the smaller-C rule. The fixed seven-value search was completed before any test predictions. No settings were changed after test results were obtained.

All three pipelines were fitted on the original 778 training windows, with balanced class weights calculated from training labels only. Scaler means and variances were verified against that partition. Their 400 test observations and row order are identical. Neither validation nor test observations were added to training. This preserves direct comparability with I.4. The selected logistic validation score was reproduced before test evaluation.

### Test results and interpretation

| Model | Accuracy | Macro precision | Macro recall | Macro-F1 | Errors |
|---|---:|---:|---:|---:|---:|
| Linear SVM | 0.8900 | 0.932927 | 0.762500 | 0.757156 | 44 |
| RBF SVM | 0.9875 | 0.985620 | 0.985417 | 0.985441 | 5 |
| Logistic regression | 0.9950 | 0.995902 | 0.995833 | 0.995842 | 2 |

Macro averages give each class equal weight; class-specific metrics include support (normal 40, each fault class 120), and undefined precision/recall/F1 values are set to zero. Confusion matrix rows are actual classes and columns predicted classes, ordered normal, inner_race, ball, outer_race. Colours and annotations use percentages within each actual class; raw counts are also shown.

Logistic regression has the highest observed test macro-F1. Linear remains the SVM selected through validation; RBF performs better on this test load. The linear model's main error is normal-to-ball (35/40 normal windows); its normal recall is 0.125 despite precision 1.0. All models send some other-class windows to ball. Logistic regression makes one inner-race-to-ball and one outer-race-to-ball error. RBF makes one normal-to-ball, one ball-to-normal and three outer-race-to-ball errors.

The test ranking is descriptive and does not initiate further tuning or replace the validation selection retrospectively. Logistic regression's advantage over RBF is three windows, not established statistical superiority. The 400 windows come from ten recordings; windows from a recording are dependent, so treating them as 400 independent trials would overstate evidence. Shared specimens, a single held-out load and I.2 full-dataset exploration also limit generalisation. Test results are now exposed and must not be reused to guide subsequent model tuning.

### Generated outputs

- `data/I5_logistic_tuning.csv`: seven validation search configurations and selection flag.
- `data/I5_model_comparison.csv`: test accuracy and macro precision, recall and F1.
- `data/I5_class_metrics.csv`: all 12 model/class combinations with support.
- `data/I5_confusion_counts.csv`: all 48 matrix entries, including zeros and row percentages.
- `data/I5_test_predictions.csv`: recording/window identifiers, actual labels and aligned predictions for each model.
- `figures_of_data/`: complete PNG tables for all five CSVs, without row splitting.
- `figures/I5_confusion_matrices.png`: three matrices with the same class order and 0–100% colour scale.

The notebook embeds the overall and per-class tables and confusion figure once, each with a preceding explanation. Its I.5 prose totals 254 words, including headings and explanations, within the 300-word limit. Prior notebook cells are unchanged. The PDF now includes Tasks I.1–I.5.

### Sources for Task I.5

[I.5-1] scikit-learn. [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). Multinomial loss, L2 regularisation, C and balanced weights. Accessed 16 November 2026.

[I.5-2] scikit-learn. [precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html). Class-specific metrics, support, macro averaging and undefined-score handling.

[I.5-3] scikit-learn. [confusion_matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html). Actual/predicted orientation and class ordering.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-16 | ChatGPT/Codex with Python and official documentation | Implement I.5 using identical features, preprocessing and test observations; compare both SVMs with validation-tuned logistic regression and explain errors within 300 words. | I.3 partitions, I.4 SVM settings, macro-F1 selection and established table/figure presentation. | Added logistic validation tuning, frozen test evaluation, overall and class-specific metrics, confusion matrices and aligned predictions; distinguished validation selection from observed test ranking. |

| 2026-11-16 | ChatGPT/Codex with Python and PDF rendering | Update the report PDF to include I.4 and I.5 using the established layout. | Notebook prose, results, A4 sizes and code-cell references. | Updated cover and linked contents, added model tables and diagnostic figures, and checked page layout; final PDF contains 28 A4 pages. |


## Task II.1 - Engineering Problem and Dataset

### Dataset reuse and prediction target

`Part_II_CNN.ipynb` starts Part II with **Option B: a compact one-dimensional convolutional neural network (1-D CNN)**. The target remains normal, inner-race fault, ball fault or outer-race fault in measured drive-end bearing vibration. These are laboratory measurements with deliberately introduced faults, not simulated records; the task is classification within that experimental scope, not remaining useful life estimation or demonstrated field diagnosis [II.1-1].

The selected dataset is unchanged, so Part I's origin, dataset citation, acquisition manifest and unresolved licence assessment are carried forward. Public download availability is not treated as a blanket reuse licence. Original recordings are unchanged, and no new dataset is acquired for II.1. The original citation remains: Case Western Reserve University, Bearing Data Center. *Bearing Data Center* [dataset]. https://engineering.case.edu/bearingdatacenter.

### Verified size and proposed neural-network inputs

The II.1 code reads the existing recording, processing, feature and split inventories without modifying them. It verifies 40 distinct recordings, 1,578 unique recording/window pairs, 12 kHz prepared sampling and the count of complete 3,000-sample windows. Normal has 138 windows; each fault class has 480. The two size counts are **40 original recordings** and **1,578 derived model observations**; neither establishes 1,578 independent bearing specimens.

The proposed CNN input for each observation is the prepared acceleration sequence, mean-centred within its existing non-overlapping 0.25-second window. It will reuse Part I's resampling, common low-pass filter and edge trimming. The planned channels-last input layout is `(1578, 3000, 1)`: windows, temporal samples and drive-end channel. At the II.1 checkpoint this was a specification; Task II.2 below constructs and verifies the tensor. The 3,000 samples are temporal input values; the eight engineered SVM descriptors are not fed to the CNN. Load, speed, defect size, recording identifiers and quality flags remain metadata.

### Architecture rationale and evaluation continuity

Conv1D applies shared convolution kernels along the temporal dimension [II.1-2]. Selecting a small 1-D CNN is our methodological inference: short vibration impulses and oscillatory patterns provide a meaningful local sequence structure, and weight sharing avoids a separate learned parameter for every temporal position. The engineering signal already has one temporal axis, so an artificial image representation is unnecessary. The choice is justified by input structure, not by an assumed performance advantage over the Part I models. Layer counts, kernel widths, regularisation, optimisation and training are deferred to later tasks. No RNN/LSTM comparison is required by the selected option.

The split inventory is retained: loads 0-1 HP provide 778 training windows; load 2 provides 400 validation windows; load 3 provides 400 test windows. All windows from each recording stay together. Any learned scaling and subsequent model selection must use training and validation data only. Window mean removal is a per-observation operation rather than a population-fitted transform. Part I has already exposed test results; the reused test load cannot be described as newly blind or used to guide CNN tuning. Shared specimens, dependent windows and a single test load continue to limit generalisation. Macro-F1 remains the planned primary selection metric.

### Generated outputs and report scope

- `Part_II_CNN.ipynb`: the II.1 report, one executed count-verification/summary-generation code cell, and one embedded summary image. At the II.1 checkpoint no tensor construction, neural-network fitting or new test evaluation had run; Task II.2 below implements the inputs and initial model.
- `data/II1_dataset_summary.csv`: the verified counts and explicitly labelled proposed CNN input specification.
- `figures_of_data/II1_dataset_summary.png`: the CSV-backed summary, with `Nb code cell 1` on its second heading line. The notebook embeds this exact PNG after its explanatory text, without a duplicate table output.

- `Part_II_CNN.pdf`: sixteen A4 portrait/landscape pages, comprising a date-free cover, linked contents and Tasks II.1-II.4; CSV-backed tables and figures have the agreed grey frames, and code is replaced by its numbered execution-label reference.

The notebook discussion is **92 words including its Part II and II.1 headings**, excluding the table, image alternative text and code. It meets the 100-word limit. Detailed source notes and methodological support are documented here. Part I notebooks, data, PNGs and PDFs are unchanged.

### Sources for Task II.1

[II.1-1] Case Western Reserve University, Bearing Data Center. [Apparatus & Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures). Laboratory motor rig, seeded defects, accelerometers, MAT recordings and documented sampling rates. Dataset citation and reuse assessment are retained from Task I.1. Accessed 18 November 2026.

[II.1-2] Keras. [Conv1D layer](https://keras.io/api/layers/convolution_layers/convolution1d/). Temporal convolution, kernel parameters and channels-last `(batch, steps, channels)` input structure. This supports the layer/input description; the application-specific suitability argument is our inference. Referencing the layer documentation does not yet fix a training framework or full architecture. Accessed 18 November 2026.

Local count and preprocessing evidence: `data/I2_recording_inventory.csv`, `data/I2_processing_summary.csv`, `data/I2_window_features.csv` and `data/I3_split_inventory.csv`; Part I notebook code cells 2-3 and 8. The saved source inventories, not the public documentation, establish the counts for this selected subset.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-18 | ChatGPT/Codex with Python and original documentation | Develop II.1 using the agreed CWRU reuse, compact 1-D CNN rationale and established notebook/table style; keep the report within 100 words. | Original recordings, prepared window definition, four classes, fixed partitions, provenance and exposed-test limitations. | Created a separate Part II notebook with a 92-word discussion, verified count summary, CSV-backed PNG and sources; deferred waveform tensor construction and neural-network training. |
| 2026-11-18 | ChatGPT/Codex with Python and PDF rendering | Generate the corresponding Part II PDF using the established report style. | The 92-word discussion, selected CNN rationale, verified summary values and notebook contents. | Created a three-page A4 PDF with cover, linked contents, framed CSV-backed table and code-cell reference; checked all table values and rendered pages. |


## Task II.2 - Data Preparation and Implementation

### Development sequence and shared preparation

The implementation contains three new notebook code cells: prepare/verify inputs (Nb code cell 2), build/check the CNN (cell 3), and save outputs/render tables (cell 4). Each step is preceded by explanatory prose, and the four embedded tables have their own preceding interpretations. II.1's 92-word report is unchanged; its summary status is explicitly scoped to that earlier checkpoint.

`signal_preparation.py` contains the original Part I signal-preparation constants and function, extracted verbatim rather than rewritten. Part I code cell 3 now imports those names; its other cells, discussion and numerical outputs are unchanged. This makes both notebooks use the same resampling, fourth-order 4.5 kHz Butterworth filter, forward/backward filtering and 0.05-second trimming at each edge. Hash verification of all 40 source files and all 1,578 reconstructed windows establishes that this refactoring preserved the audited observations.

For each cached MAT file, the saved selected DE variable and documented sample rate are read from the Part I inventory. Normal recordings are resampled from 48 to 12 kHz; fault recordings remain at 12 kHz. Complete non-overlapping 3,000-sample windows are reconstructed using their saved recording/window keys. Their float64, little-endian hashes are checked before centring, standardisation or float32 conversion. No raw source files are changed or downloaded again.

### Partitions, targets and leakage controls

The existing split inventory is joined by recording ID and window index, never by coincidental CSV order. Every source key is covered once. Loads 0-1 HP supply training data, load 2 supplies validation data and load 3 supplies the later evaluation set. Assertions verify no shared recordings or original window hashes across partitions and all-class coverage.

| Partition | Recordings | Windows | Input shape | Normal | Inner race | Ball | Outer race |
|---|---:|---:|---|---:|---:|---:|---:|
| Training | 20 | 778 | `(778, 3000, 1)` | 58 | 240 | 240 | 240 |
| Validation | 10 | 400 | `(400, 3000, 1)` | 40 | 120 | 120 | 120 |
| Test | 10 | 400 | `(400, 3000, 1)` | 40 | 120 | 120 | 120 |

Targets are int64 class indices: normal=0, inner_race=1, ball=2, outer_race=3. No one-hot encoding is needed for sparse categorical cross-entropy [II.2-4]. The 3,000 temporal acceleration values form the one-channel input; the eight engineered SVM descriptors and operating/identity metadata are excluded from predictors. Window dependence and shared specimens remain limitations.

Each window is mean-centred independently, then one channel mean and population standard deviation are calculated using the 2,334,000 acceleration samples in the 778 training windows. The fitted mean is **1.5853023930246317e-19** and standard deviation **0.34132989120121204**. The common transformation `(centred acceleration - training mean) / training std` is applied to all three partitions before float32 conversion. No validation/test samples contribute to these two statistics. The small training mean reflects the preceding window mean removal; individual window standard deviations are not normalised away. The scaled training mean is approximately 1.48e-11 and standard deviation approximately 1. Inputs are finite float32 tensors; target ranges and tensor shapes are checked.

### Working CNN and architecture summary

A Keras Sequential model has the following initial architecture [II.2-1, II.2-2, II.2-3]. Output dimensions omit the batch axis in this compact description; the complete CSV/PNG includes it as `None`.

| Component | Settings | Output | Trainable parameters |
|---|---|---|---:|
| Input | 3,000 time steps, one acceleration channel | `3000 x 1` | 0 |
| Conv1D + ReLU | 16 filters, kernel 15, stride 1, same padding, biases | `3000 x 16` | 256 |
| MaxPooling1D | Pool/stride 4, valid padding | `750 x 16` | 0 |
| Conv1D + ReLU | 32 filters, kernel 7, stride 1, same padding, biases | `750 x 32` | 3,616 |
| GlobalAveragePooling1D | Temporal mean of each feature map | `32` | 0 |
| Dense + softmax | Four units and biases | `4` | 132 |
| Total | Two convolutional layers | `4` | **4,004** |

The convolutions learn local patterns and their combinations. Max pooling reduces the intermediate sequence length; global averaging aggregates features without a large flattened head. The specific filter counts and kernel widths are initial design decisions, not tuned optima. The architecture summary is an explicit II.2 output, generated from the actual layer shapes and trainable weights. Independent arithmetic checks include biases: `(15*1+1)*16 + (7*16+1)*32 + (32+1)*4 = 4004`. There are no non-trainable model parameters.

The model is compiled with Adam at a provisional learning rate of 0.001 and sparse categorical cross-entropy on softmax probabilities. Seed 550 is recorded and deterministic TensorFlow operations are requested [II.2-4, II.2-6]. Initialising the optimiser's zero state supports faithful model serialisation without applying updates. An eight-observation training batch produces finite `(8,4)` probabilities in [0,1] with row sums of one and finite loss. Initial loss is a numerical readiness check, not an accuracy or generalisation result. All initial weights are unchanged, and the optimiser iteration count is **zero**. Gradient/update checks and training schedules remain for the later training task.

The input archive is reopened and compared element-for-element. The complete `.keras` model is reloaded, its weights are compared exactly, and its training-batch probabilities reproduce [II.2-5]. No `fit`, optimiser update, validation/test prediction or test performance score is executed in II.2. Part I's previously examined test results do not guide the CNN settings; the reused test set is not described as newly blind. Macro-F1 remains the planned selection metric for later tasks.

### Outputs and reproduction

See [Execution Instructions](#execution-instructions) for the runtime, execution order and reproduction notes.

- `data/II2_model_inputs.npz`: one compressed archive containing `X_`, `y_` and `row_index_` arrays for training, validation and test. Waveforms are float32 and targets int64.
- `data/II2_input_inventory.csv`: global row index, recording/window keys, target, load, partition and original window hash. The archive row indices link back to this inventory.
- `data/II2_preparation_metadata.json`: one record of the scaling statistics, class mapping, split counts, source hashes, module hash, seed, versions, readiness checks, initial-state status and saved-artifact fingerprints.
- `models/II2_initial_model.keras`: one complete, compiled model archive with **initial, untrained** weights and optimiser state; training remains deferred.
- `data/II2_partition_summary.csv`, `II2_target_mapping.csv`, `II2_preprocessing_checks.csv`, `II2_architecture_summary.csv`: complete supporting tables. Their corresponding PNGs in `figures_of_data/` are embedded exactly once in the notebook, after their explanations. Stored CSV values are not rounded.

The architecture table includes every layer's settings, output shape and trainable count; the total row is a summary and must not be added again when summing per-layer counts. The preparation table contains the fit statistics and check results; the label table makes class encoding explicit. No redundant notebook table displays or model-summary printout repeat these images. The report PDF now covers II.1-II.4 in sixteen A4 pages, with the architecture summary, supporting tables, learning curves and test results; code blocks are replaced by execution-labelled references. Both report covers follow the agreed Part I style without dates.

### Sources for Task II.2

[II.2-1] Keras. [The Sequential model](https://keras.io/guides/sequential_model/). Linear stacks of layers and explicit input shapes. Accessed 18 November 2026.

[II.2-2] Keras. [Conv1D layer](https://keras.io/api/layers/convolution_layers/convolution1d/). Filters, kernels, stride, padding, activations and temporal input layout. Accessed 18 November 2026.

[II.2-3] Keras. [MaxPooling1D](https://keras.io/api/layers/pooling_layers/max_pooling1d/) and [GlobalAveragePooling1D](https://keras.io/api/layers/pooling_layers/global_average_pooling1d/). Temporal downsampling and feature aggregation. Accessed 18 November 2026.

[II.2-4] Keras. [Probabilistic losses](https://keras.io/api/losses/probabilistic_losses/), SparseCategoricalCrossentropy. Integer targets and probability-based cross-entropy. Accessed 18 November 2026.

[II.2-5] Keras. [Whole model saving & loading](https://keras.io/api/models/model_saving_apis/model_saving_and_loading/). A single `.keras` archive stores architecture, weights and optimiser state. Accessed 18 November 2026.

[II.2-6] Keras. [set_random_seed](https://keras.io/api/utils/python_utils/#set_random_seed-function). Random-seed control and reproducibility limits. Accessed 18 November 2026.

Signal preparation and provenance follow Part I's original sources and audit, not a newly selected dataset. The application-specific rationale for a compact CNN is our inference from the temporal vibration structure, rather than a performance claim established by these API references.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-18 | ChatGPT/Codex with Python, TensorFlow/Keras and original documentation | Implement the simplified II.2 plan, explain the development steps clearly, provide an explicit architecture summary and add useful non-duplicated tables. | Same recordings, 1,578 windows, fixed load partitions, four classes, two-convolution architecture and leakage controls. | Shared the original signal-preparation function; verified 40 file and 1,578 window hashes; built/scaled tensors and the 4,004-parameter initial CNN; added four CSV-backed tables, one input archive, metadata JSON and a reload-verified model. No fitting or test scoring ran. |

| 2026-11-18 | ChatGPT/Codex with Python and PDF rendering | Update both PDFs with the shared-module explanations and include completed II.2. | Existing numerical results, compact CSV-backed tables, grey frames and execution-labelled code references. | Updated Part I in 28 A4 pages and Part II through II.2 in seven A4 pages; matched date-free covers and verified contents links, all II.2 prose and all 154 Part II table cells. |


## Task II.3 - Training and Evaluation

### Protocol fixed before training

The simplified plan uses one pre-specified seeded run, one custom callback, three principal result tables and two figures. The II.2 prepared tensors, training-only scaling, class mapping and two-convolution architecture are unchanged. Training starts from `models/II2_initial_model.keras`, whose saved fingerprint and zero optimiser iteration count are verified. Training and validation arrays are loaded first; test arrays are accessed only after checkpoint selection is complete.

| Setting | Fixed value |
|---|---|
| Optimiser | Adam, learning rate 0.001 |
| Loss | Sparse categorical cross-entropy on four softmax probabilities |
| Batch size | 32 |
| Maximum epochs | 100 |
| Random seed | 550 |
| Class weights | normal: 3.353448275862069; each fault class: 0.8104166666666667 |
| Selection | Highest validation macro-F1; strict improvement; exact ties retain earlier epoch |
| Stopping | 15 consecutive epochs without strictly higher validation macro-F1, or epoch 100 |
| Splits | Training 778 windows; validation 400; test 400 |

Weights use `778 / (4 * training_class_count)`, with 58 normal and 240 windows for each fault class. They balance total class contributions to the training objective without changing or resampling the held-out distributions. Adam and sparse categorical cross-entropy retain the II.2 implementation [II.3-1, II.3-2]. Training windows are shuffled by a seeded `tf.data.Dataset` each epoch; the notebook explicitly sets `fit(shuffle=False)` because the dataset supplies the shuffle. The original run used the default fit argument, which Keras ignored for this dataset; the explicit argument removes that warning without changing the effective training procedure or results. Deterministic TensorFlow operations are requested and the existing framework versions remain those recorded for II.2.

### One callback, comparable learning curves and stopping

The custom callback runs after each epoch using the completed epoch's weights in inference mode. It obtains training and validation probabilities, computes unweighted cross-entropy and macro-F1, records the epoch and saves the complete model only on a strictly higher validation macro-F1 [II.3-3]. All four labels are included, and undefined class scores are zero. A non-finite training/validation value raises an error.

The weighted batch optimisation loss from Keras is stored separately as `weighted_optimization_loss`. It is not compared directly with unweighted validation loss in the plot. Instead, both plotted losses are unweighted and recomputed after the epoch, using the same weights. The second panel plots training/validation macro-F1. The selected epoch is marked in both panels. This separates probability-sensitive cross-entropy from decision-based F1: probabilities and loss can improve without changing the class argmax. No optimiser search, learning-rate schedule, architecture change or repeated-seed selection is performed.

Training completed **46 epochs**, stopping after 15 consecutive epochs failed to exceed the epoch-31 validation macro-F1. Epoch **31** was selected with training macro-F1 **0.9916643512**, validation macro-F1 **0.9686842151**, training loss **0.0818050727** and validation loss **0.1062805206**. By epoch 46, training macro-F1 was 0.9968748779 and validation macro-F1 0.9580419580. The last epoch's slightly lower validation loss (0.1060379595) did not change the macro-F1 selection rule. The chosen checkpoint contains 775 Adam updates: 31 epochs times 25 training batches. The final in-memory epoch is not used for test evaluation; the selected checkpoint is reloaded and its validation macro-F1 reproduced first.

### Classification evaluation and interpretation

MAE and RMSE are not reported: this is categorical classification rather than regression/forecasting of a numerical quantity. Integer targets 0-3 encode class identity and have no meaningful numerical distance. The notebook retains the explicit justification in the evaluation explanation. Accuracy, macro precision, macro recall, macro-F1, per-class scores/support and a confusion matrix satisfy the classification requirements [II.3-4, II.3-5].

| Metric | Selected CNN, test load 3 HP |
|---|---:|
| Accuracy | 0.8300000000 |
| Macro precision | 0.8489602559 |
| Macro recall | 0.8583333333 |
| Macro-F1 | 0.8518515860 |
| Test windows / errors | 400 / 68 |

| Actual class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| normal | 0.9302325581 | 1.0000000000 | 0.9638554217 | 40 |
| inner_race | 0.7619047619 | 0.6666666667 | 0.7111111111 | 120 |
| ball | 1.0000000000 | 0.9750000000 | 0.9873417722 | 120 |
| outer_race | 0.7037037037 | 0.7916666667 | 0.7450980392 | 120 |

One logical inference pass over the 400 test windows produces the stored probabilities and labels. All metrics and confusion entries derive from that same prediction inventory. Matrix rows are actual classes and columns predictions, ordered normal, inner_race, ball, outer_race. The 0-100% colour scale uses percentages within each actual class, and annotations give both counts and percentages.

The 68 errors consist of 40 inner-race-to-outer-race, 25 outer-race-to-inner-race and three ball-to-normal predictions. All errors occur in the three 0.014-inch fault recordings under 3 HP: recording 172 contributes all 40 of its windows, recording 200 contributes 25 of 40, and recording 188 contributes three of 40. This identifies a condition-specific cross-load weakness without establishing its cause. In particular, the 68 errors should not be treated as 68 independent bearing failures. Normal recall is 1.0, although the three ball-to-normal predictions reduce normal precision.

Training and validation performance are higher than test performance. Continued training after the selected epoch reduced training loss without exceeding the validation macro-F1; a fitting/validation gap can reflect both fitting behaviour and operating-condition shift. Shared specimens, dependent windows within ten test recordings, one test load and the already examined Part I test results limit generalisation. One seeded run does not establish robustness across initialisations. No CNN setting or selected epoch is revised after seeing the test results.

### Saved outputs and notebook presentation

- `models/II3_selected_model.keras`: the single selected trained checkpoint, including its optimiser state; it does not replace the initial II.2 model.
- `data/II3_epoch_history.csv`: all 46 epochs, weighted optimisation loss, unweighted epoch-end training/validation losses, macro-F1 values and strict-best flags.
- `data/II3_run_metadata.json`: the protocol written before training, initial/input hashes, selected epoch, actual stopping reason, selected-model fingerprint, timing, versions and frozen test results. The final `test_inference_passes` value is 1.
- `data/II3_training_summary.csv`, `II3_test_metrics.csv`, `II3_class_metrics.csv`: the three principal tables, with full stored precision and four-decimal metric displays in their PNG counterparts.
- `data/II3_confusion_counts.csv`: all 16 matrix entries, including zero counts and row percentages.
- `data/II3_test_predictions.csv`: all 400 aligned test observations, original recording/window keys, actual/predicted classes and all four probabilities.
- `figures/II3_learning_curves.png` and `II3_confusion_matrix.png`: the two required figures, with consistent two-line headings, spacing and notebook code cell 7 references.

Three new main notebook code cells train/select (Nb code cell 5), evaluate (cell 6), and save/render (cell 7). Explanations cover the steps, reasoning, class weights, loss/metric distinction, stopping, classification metrics, errors and limitations. The three table PNGs and two figures are each embedded once after a dedicated explanation. The prediction inventory remains a supporting CSV. II.1's 92-word discussion and all II.2/Part I numerical artifacts are unchanged. The updated PDF covers Tasks II.1-II.4 in sixteen A4 pages, including the training protocol, MAE/RMSE justification, learning curves, test metrics, confusion matrix and interpretation of the concentrated errors.

### Sources for Task II.3

[II.3-1] Keras. [Adam](https://keras.io/api/optimizers/adam/). Adaptive moment estimates and optimiser configuration. Accessed 18 November 2026.

[II.3-2] Keras. [Probabilistic losses](https://keras.io/api/losses/probabilistic_losses/), SparseCategoricalCrossentropy, and [model training APIs](https://keras.io/api/models/model_training_apis/). Integer classification targets, weighting and dataset-based training. Accessed 18 November 2026.

[II.3-3] Keras. [Writing your own callbacks](https://keras.io/guides/writing_your_own_callbacks/) and [EarlyStopping](https://keras.io/api/callbacks/early_stopping/). Epoch-end hooks, checkpointing and stopping concepts. The notebook implements the strict macro-F1 rule in one custom callback, rather than combining several callbacks. Accessed 18 November 2026.

[II.3-4] scikit-learn. [precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html) and [f1_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html). Class scores, support, macro averages and undefined-score handling. Accessed 18 November 2026.

[II.3-5] scikit-learn. [confusion_matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html). Actual/predicted orientation and fixed label ordering. Accessed 18 November 2026.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-18 | ChatGPT/Codex with Python, TensorFlow/Keras and original documentation | After explicit Proceed, implement the simplified II.3 plan with clear explanations of steps, reasoning, theory and stopping; retain the MAE/RMSE justification. | II.2 inputs, training-only scaling, fixed partitions, four classes, 4,004-parameter architecture and one seeded protocol. | Trained 46 epochs, selected epoch 31 by validation macro-F1, froze and scored the test set once; added learning curves, required classification results, three CSV-backed tables, trained checkpoint, history/metadata and aligned predictions. No test-guided tuning followed. |
| 2026-11-18 | ChatGPT/Codex with Python and PDF rendering | Update the Part II PDF after completing II.3. | Existing II.1-II.2 report pages, date-free cover style, compact tables, grey frames and execution-labelled code references. | Added II.3 in four pages; checked all 54 new table values, seven code references, ten frames and three contents destinations, and visually reviewed the new pages. |

## Task II.4 - Model Behavior

### Option B - Prediction Errors

II.4 analyses the test predictions saved in II.3. “Frozen predictions” means retaining those predictions and the epoch-31 selected model, with no retraining, additional inference or test-guided adjustment. Notebook code cell 8 is a standalone analysis of saved CSVs; it does not load TensorFlow or the model. See [Execution Instructions](#execution-instructions) for running II.4 independently from saved artifacts.

The code checks that the 400 prediction row indices uniquely and completely match the II.2 test inventory, verifies recording/window/class identities and test load, and joins the audited recording metadata. It aggregates all ten test recordings, including successes, into error counts, percentages and wrong-label destinations. Source fingerprints verify that the inputs, predictions, metrics and checkpoint remain unchanged.

Recording 172 (inner race, 0.014 inches) has 40/40 errors, all predicted outer race; recording 200 (outer race, 0.014 inches) has 25/40 errors, all predicted inner race; recording 188 (ball, 0.014 inches) has 3/40 errors, all predicted normal. The other seven recordings have no errors. Inner/outer confusions account for 65/68 errors (95.6%). The table and plot include every recording, rather than selecting only failures.

The notebook distinguishes measured findings from hypotheses about operating-condition changes and the learned representation. All test records have the same nominal 3 HP load, and outer-race position is fixed, so these variables alone do not explain the concentration. No causal or signal-similarity experiment is claimed. Dependent windows, one recording per condition/diameter at the test load, shared specimens and one seeded model limit generalisation. The architecture and test results remain unchanged; Option A's complexity comparison and repeated seeds are not required for the chosen Option B.

### Generated outputs

- `data/II4_recording_errors.csv`: all ten test recordings, condition, fault diameter, load, window count, errors, error percentage and wrong-label counts.
- `data/II4_analysis_metadata.json`: source SHA-256 fingerprints, alignment checks and analysis totals.
- `figures_of_data/II4_recording_errors.png`: CSV-backed recording table; heading identifies Task II.4 and Nb code cell 8.
- `figures/II4_recording_errors.png`: recording-level error-rate chart, with counts and the established two-line plot heading.

Each image is embedded once after its explanation. Code cell 8 produces no duplicate table or plot output. The PDF now covers II.1-II.4 in sixteen A4 pages, including the recording table, error-rate figure and full interpretation. The linked contents and date-free cover reflect II.4.

### References

[II.4-1] Case Western Reserve University Bearing Data Center. [Apparatus & Procedures](https://engineering.case.edu/bearingdatacenter/apparatus-and-procedures). Test apparatus, accelerometer measurements and influence of outer-race position relative to the load zone. Accessed 18 November 2026.

[II.4-2] Case Western Reserve University Bearing Data Center. [12k Drive End Bearing Fault Data](https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data). Load/speed conditions and outer-race positions; the selected files use the 6 o'clock position. Accessed 18 November 2026.

### AI Log

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-18 | ChatGPT/Codex with Python and CWRU documentation | After explicit execution instruction, implement Option B, explain frozen predictions briefly, and provide an evidence-based error analysis. | Saved II.3 predictions, selected model, partitions, earlier notebook cells and numerical results. | Added code cell 8, checked recording joins, all-ten-recording table and error-rate figure, source hash audit, clear explanations, engineering hypotheses and limits. No retraining, inference or model tuning. |
| 2026-11-18 | ChatGPT/Codex with Python and PDF rendering | Update the Part II PDF to include II.4. | Existing II.1-II.3 body pages, formatting, grey frames and code references. | Added three II.4 pages; verified all II.4 prose and 80 table values, eight code references, twelve frames and four contents destinations; visually reviewed the new pages. |

## Part I - Output regeneration notes

The setup cell now creates `data`, `figures` and `figures_of_data`, including when these directories have been removed. The ten I.2/I.3 CSV tables previously had no notebook rendering calls; they now use the early `render_data_table` helper immediately after each CSV is written. It retains every row and CSV value, the two-line title with the existing notebook code-cell number, and the established table colours. Existing I.4/I.5 table rendering remains in place. The analytical calculations, splits and model settings are unchanged.

For the rebuild and attachment-refresh steps, see [Execution Instructions](#execution-instructions).

### AI Log - Part I regeneration fix

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-19 | ChatGPT/Codex with Python | Fix Part I output regeneration, create missing folders, add missing table rendering, explain attachment refresh and verify a clean rebuild. | Existing analysis, partitions, model settings, code-cell order and numerical results. | Added early CSV table renderer and ten I.2/I.3 calls, automatic table-folder creation, explicit image-source metadata and a separate attachment refresh utility; documented the rebuild sequence. |

Validation: executed every Part I code cell in an isolated directory initially containing only the notebook, shared preparation module and original source cache. Recreated all 17 CSVs, 17 table PNGs and eight plots. All CSV values matched the existing results (floating-point tolerance 1e-10 relative, 1e-12 absolute). Verified all 18 refreshed attachments exactly match their source PNGs and that refreshing preserves cell source and saved outputs.

Documentation update (19 November 2026): consolidated setup, Part I/Part II execution order, clean regeneration, Part I attachment refresh, standalone II.4 execution and PDF export guidance under Execution Instructions. No notebook code or numerical artifacts changed.

### AI Log - Part II attachment refresh

| Date | Tool used | Essence of major prompts | What was kept | What was changed |
|---|---|---|---|---|
| 2026-11-19 | ChatGPT/Codex with Python | Implement the agreed full-run workflow, Part II attachment refresh and consolidated execution sequence with considerations below and no bold text. | CNN architecture, training/evaluation rules and existing numerical artifacts. | Added Part II image-source metadata and refresh command reusing the Part I helper; reorganised Execution Instructions and tested a full isolated Part II rebuild. |

Part II repair validation: ran all eight code cells in an isolated copy containing original recordings and Part I CSVs, with no Part II results or images initially present. Recreated all 13 Part II CSVs, nine table PNGs and three plot PNGs, plus the input archive, metadata and initial/selected model files. Verified all 12 refreshed attachments exactly match their external PNGs; refresh preserved cell source, saved outputs, data and model hashes. A missing-image check failed before writing and left the notebook unchanged. The project’s existing CNN training (and evaluation) results were preserved; the verification run remained isolated.

PDF update (19 November 2026): both reports now include the current Execution Instructions as a linked appendix. Part I contains 30 A4 pages; Part II contains 16 A4 pages. Existing report body pages, compact tables, figures and grey frames were preserved. Complete appendix wording, A4 page sizes, contents destinations and page numbering were checked.
