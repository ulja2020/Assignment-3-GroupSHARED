# Assignment 3 development

## Folder conventions

- `public_dataset/`: all original downloads and accompanying source materials; preserve raw recordings unchanged.
- `figures/`: PNG outputs produced by our code only.
- `data/`: CSV outputs produced by our code only.
- Notebook and documentation: directly within mother folder.

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

Open `Part_I_SVM.ipynb` with `draft-A` as the working directory and run cells in order. Install the recorded dependencies from `requirements.txt` if necessary. Acquisition cells use the original CWRU URLs and reuse locally cached files after checksum verification. Raw data total approximately 140 MB and are excluded from version control; acquisition code is contained in the notebook. All generated CSVs and PNGs are reproducible from the retained original recordings. The notebook retains its executed tables and images.

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
