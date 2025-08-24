# Web Scrapping

This folder contains scripts for collecting abstracts and plain language summaries from the Cochrane Library, as well as downloading Pfizer documents. The objective is to gather data for further analysis and processing.

## Scripts

### cochrane_collector.py

This script collects abstracts and plain language summaries (PLS) from the Cochrane Library based on DOIs listed in `doi.txt`. 

#### Steps:
1. **Initialize WebDriver**: Uses Selenium to control a web browser.
2. **Read DOIs**: Reads DOIs from `doi.txt`.
3. **Scrape Data**: For each DOI, navigates to the corresponding Cochrane page, scrapes the abstract and PLS sections, and saves them to text files.
4. **Logging and Error Handling**: Logs each successfully processed DOI and records errors in separate error logs.

#### Usage:
1. Place DOIs in `doi.txt`.
2. Run the script to start collecting data.

### pfizer_document_collector.py

This script downloads plain language study result summaries and associated documents from the Pfizer website.

#### Steps:
1. **Initialize WebDriver**: Uses Selenium to control a web browser.
2. **Scrape URLs**: Collects URLs for download links and PLS pages.
3. **Download PDFs**: Downloads PDF documents based on the collected URLs.
4. **Save Links and Documents**: Saves the download URLs, PLS URLs, and NCT IDs to `links_documents_pfizer.txt` and the downloaded PDFs to the `pfizer_documents` folder.

## Folders

### abstracts/
Contains the abstract text files collected from the Cochrane Library.

### pls/
Contains the plain language summaries collected from the Cochrane Library.

### errors/
Contains error logs for failed attempts to scrape abstracts or PLS sections.

### pfizer_documents/
Contains the downloaded Pfizer documents in PDF format.

## Files

### doi.txt
A text file containing DOIs for Cochrane Library entries to be processed.

### links_documents_pfizer.txt
A text file containing URLs and NCT IDs for the Pfizer documents.

### log.txt
A log file recording each successfully processed DOI from the Cochrane Library script.