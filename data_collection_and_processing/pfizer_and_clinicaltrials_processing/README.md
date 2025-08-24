# Pfizer Processing Folder

The `pfizer_processing` folder contains several subfolders and files that facilitate the processing, extraction, and correction of text from Pfizer documents and clinical trials. Below is a detailed explanation of each important file and folder.

## clinical_trials_extraction.ipynb

This notebook is designed to interact with the Clinical Trials API to retrieve and process clinical trial information based on NCT IDs. The steps include:

1. **Importing Necessary Libraries**: `numpy`, `os`, `requests`, and `json`.
2. **Defining Functions**:
    - `get_trials(expr)`: Retrieves trial IDs based on a search expression.
    - `get_clinical_trials(nct_id)`: Fetches detailed information for a given NCT ID.
    - `save_clinical_trials(nct_id)`: Saves the detailed trial information into text files.
    - `save_text(text, filename)`: Utility function to save text to a file.
3. **Extracting NCT IDs**: From filenames in the `full_texts` directory.
4. **Saving Detailed Information**: For each NCT ID, detailed trial information is saved into the `ncts` directory.

## pfizer_text_correction_with_gpt35.ipynb

This notebook uses the GPT-3.5 model to correct writing errors in Pfizer text documents without changing the original wording. The workflow includes:

1. **Importing Libraries**: `os` and `openai`.
2. **Setting Up OpenAI API**: Configuring the API key, base URL, type, version, and deployment name.
3. **Loading Text Files**: Reading text files from the `fragments/second_section` directory.
4. **Processing Text with GPT-3.5**: Sending each text fragment to the GPT-3.5 model for correction and saving the corrected text to `fragments/second_section_corrected`.

## regex_extractor.py

This Python script uses regular expressions to extract specific sections of text from files in the `full_texts` directory. The extracted text is saved into the `fragment` directory. The steps include:
1. **Importing Libraries**: `re` and `os`.
2. **Listing Text Files**: Getting all files in the `full_texts` directory.
3. **Extracting Text with Regex**: Using a regex pattern to find text between "What happened during the study?" and "What were the results of the study?".
4. **Saving Extracted Text**: Writing the extracted text to new files in the `fragment` directory.

## data_augmentation.py

The `get_paragraphs` function processes a text file, splitting its content into paragraphs and saving specific paragraphs or groups of paragraphs based on their length. Here’s a step-by-step explanation:

1. **Read the File**: 
   - The function opens the specified input file and reads its content into a variable named `content`.

2. **Split into Paragraphs**:
   - The content is split into paragraphs based on newline characters (`\n`), and any trailing empty paragraph is removed.

3. **Process Each Paragraph**:
   - The function iterates over each paragraph. 
   - If a paragraph is empty, it is skipped.

4. **Save Long Paragraphs**:
   - If a paragraph contains more than 250 words, it is saved as a separate file named with the suffix `_section{i+1}.txt`.

5. **Accumulate and Save Paragraphs**:
   - Paragraphs are accumulated into a variable `text`.
   - If the accumulated text increases by more than 50 words and exceeds 250 words, and it is not the last paragraph, it is saved as a separate file named with the suffix `_accumulated_section{i+1}.txt`.

6. **Completion Message**:
   - After processing all paragraphs, a completion message is printed.
