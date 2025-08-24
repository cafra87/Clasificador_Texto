# Data Sources

The `Data Sources` folder contains datasets from various sources, including ClinicalTrials.gov, Cochrane, Pfizer, and Trial Summaries. These datasets are organized into folders and subfolders, each containing text data used for training and testing machine learning models.

## Contents

### Cochrane

The Cochrane dataset is divided into two main folders: `train` and `test`.

#### Train

- **non_pls**: 6641 texts
- **non_pls aumented**: 24477 texts
- **non_pls total**: 31118 texts
- **pls**: 4496 texts
- **pls aumented**: 11745 texts
- **pls total**: 16241 texts

#### Test

- **non_pls**: 1661 texts
- **non_pls aumented**: 6003 texts
- **non_pls total**: 7664 texts
- **pls**: 1124 texts
- **pls aumented**: 2816 texts
- **pls total**: 3940 texts

### Pfizer

The Pfizer dataset has three folders:

- **original_pfizer_texts**: Contains 130 PDFs with Original Plain Language Study Results Summaries from Pfizer.
- **test**: Contains 117 texts extracted from the original PDFs and augmented by paragraphs.
- **train**: Contains 491 texts extracted from the original PDFs and augmented by paragraphs.

### Trial Summaries

The Trial Summaries dataset includes texts in plain language and is organized into four folders:

#### original_texts

- **alx**: 6 PDFs with clinical results by Alexion
- **amg**: 16 PDFs with clinical results by Amgen
- **ast**: 202 PDFs with clinical results by Astellas Pharma
- **csl**: 9 PDFs with clinical results by CSL Bering
- **gsk**: 95 PDFs with clinical results by GSK
- **ins**: 1 PDF with clinical results by Inside
- **lbi**: 1 PDF with clinical results by Lung Biotechnology
- **med**: 290 PDFs with clinical results by AstraZeneca and MedImmune
- **sep**: 1 PDF with clinical results by Sunovion
- **viv**: 12 PDFs with clinical results by ViiV Healthcare

#### not_taken_texts

Contains texts that were not selected for further processing.

#### med

Contains 979 texts extracted from the `med` documents.

#### alx

Contains 57 texts extracted from the `alx` documents.

### ClinicalTrials.gov

The ClinicalTrials.gov dataset is organized into two folders, with data extracted using the NCT of the Pfizer documents:

#### train

Contains 623 texts extracted from the API and augmented by paragraphs similar to the Pfizer folder.

#### test

Contains 130 texts extracted from the API and augmented by paragraphs similar to the Pfizer folder.
