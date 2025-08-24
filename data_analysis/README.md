### Data Analysis Folder

The `data_analysis` folder is organized to facilitate the analysis and modeling of text data for readability and plain language detection. This folder contains cleaned datasets, results of various hypothesis tests, notebooks for performing the analysis and modeling.

## Contents

### data_clean Directory

The `data_clean` directory contains cleaned datasets used for training and testing machine learning models, as well as for performing hypothesis tests. The files include:

- **data_no_plain_test.csv**: Test dataset containing non-plain language texts.
- **data_plain_test.csv**: Test dataset containing plain language texts.
- **data_test.csv**: General test dataset.
- **data_train.csv**: Training dataset.
- **emv_weights.csv**: Weights calculated for each feature based on the EMV metric.
- **readability_results_clean.csv**: Cleaned results from readability tests.

### test_results Directory

The `test_results` directory stores the results of various hypothesis tests conducted to determine the significance of different features in distinguishing between plain and non-plain language texts. The results are saved in both JSON and text formats for easy reference and further analysis. The files include:

- **ks.json**: JSON file containing the results of the Kolmogorov-Smirnov test.
- **ks.txt**: Text file containing the results of the Kolmogorov-Smirnov test.
- **mannwhitneyu.json**: JSON file containing the results of the Mann-Whitney U test.
- **mannwhitneyu.txt**: Text file containing the results of the Mann-Whitney U test.
- **wilcoxon.json**: JSON file containing the results of the Wilcoxon test.
- **wilcoxon.txt**: Text file containing the results of the Wilcoxon test.

### Notebooks

Two notebooks are included in the `data_analysis` folder, each serving a specific purpose in the analysis and modeling process:

- **hypothesis_tests.ipynb**: This notebook is dedicated to performing various hypothesis tests on the features to determine their significance in distinguishing between plain and non-plain language texts. The tests include Kolmogorov-Smirnov, Mann-Whitney U, and Wilcoxon tests. The results are stored in the `test_results` directory.
- **models.ipynb**: This notebook focuses on building and evaluating machine learning models for predicting whether a text is plain or non-plain language. It includes:
  - Loading and preprocessing the data.
  - Implementing a custom model using an EMV-based metric.
  - Training and evaluating GradientBoosting and RandomForest models.
  - Selecting relevant features based on their importance.

