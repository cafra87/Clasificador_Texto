# Import necessary libraries
from selenium import webdriver
from bs4 import BeautifulSoup

# Initialize the Selenium webdriver
driver = webdriver.Chrome()

# Define the base URL for the Cochrane Library
base_url = "https://www.cochranelibrary.com/cdsr/doi/{}/full"

# Initialize an empty list to store DOIs
DOIs = []

# Open the file containing DOIs
with open('doi.txt', 'r') as file:
   # Read each line of the file
   for line in file.readlines():
       # Append each DOI to the list
       DOIs.append("{}".format(line.strip()))

# Initialize the counter
i = 0

# Loop through each DOI
for doi in DOIs:
   # If the counter reaches 9000, stop the loop
   if i == 9000:
       break

   # Navigate to the page for the current DOI
   driver.get(base_url.format(doi))

   # Clean the DOI
   doi_clean = "-".join(doi.split("/"))

   try:
       # Get the HTML of the page
       html = driver.page_source
       # Parse the HTML with BeautifulSoup
       soup = BeautifulSoup(html, features="html.parser")
   except:
       # If there's an error, print the DOI and continue to the next iteration
       print("Error getting page: ", doi)
       continue

   # Try to find and save the abstract
   try:
       # Find the abstract section
       abstract = soup.find("section", {"class": "abstract"})
       abstract_division = abstract.find("div", {"class": "abstract full_abstract"})

       # Define the filenames for the abstract and error logs
       name_file_abstract = f"abstracts/{doi_clean}-abstract.txt"
       name_file_error_abstract = f"errors/abstract-errors.txt"

       # Open the file for writing
       with open(name_file_abstract, "w", encoding='utf-8') as f:
           # Loop through each section and paragraph in the abstract
           for s in abstract_division.find_all("section"):
               for t in s.find_all("h3"):
                  f.write(t.text + "\n")
               for p in s.find_all("p"):
                  f.write(p.text + "\n")
   except:
       # If there's an error, print the DOI and write it to the error log
       print("Abstract: ", doi)
       with open(name_file_error_abstract, "a", encoding='utf-8') as f:
           f.write(f"{i} Abstract: "+doi +"\n")

   # Try to find and save the PLS
   try:
       # Find the PLS section
       pls = soup.find("section", {"class": "pls"})
       pls_division = pls.find("div", {"class": "abstract abstract_plainLanguageSummary"})

       # Define the filenames for the PLS and error logs
       name_file_pls = f"pls/{doi_clean}-pls.txt"
       name_file_error_pls = f"errors/pls-errors.txt"

       # Open the file for writing
       with open(name_file_pls, "w", encoding='utf-8') as f:
           # Loop through each heading and paragraph in the PLS
           for t in pls_division.find_all("h3"):
               f.write(t.text + "\n")
           for p in pls_division.find_all("p"):
               f.write(p.text + "\n")
   except:
       # If there's an error, print the DOI and write it to the error log
       print("PLS: ", doi)
       with open(name_file_error_pls, "a", encoding='utf-8') as f:
           f.write(f"{i} PLS: "+doi + "\n")

   # Write a log entry
   with open("log.txt", "a", encoding='utf-8') as f:
       f.write(f"{i+1}: "+doi + " logged!" + "\n")

   # Increment the counter
   i += 1
