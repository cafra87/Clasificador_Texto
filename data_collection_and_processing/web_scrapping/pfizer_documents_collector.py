
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# Initialize a Chrome WebDriver instance
driver = webdriver.Chrome()

# Define the main URL and the second URL
main_url = 'https://www.pfizer.com'
second_url = '/science/clinical-trials/plain-language-study-results-summaries?sort_by=field_medicine&items_per_page=48&search_api_fulltext=&page='

# Initialize two empty lists to store the download URLs and the PLS URLs
download_urls = []
pls_urls = []

# Open a file named 'links_documents_pfizer.txt' in write mode and clear its contents
with open('links_documents_pfizer.txt', 'w', encoding='utf-8') as f:
   f.write("")

# Loop over the range 0 to 5
for i in range(0, 6):
   # Get the page source of the current page
   driver.get(main_url + second_url + str(i))
   html = driver.page_source
   # Parse the page source with BeautifulSoup
   soup = BeautifulSoup(html, features="html.parser")
   # Loop over all div elements with class 'views-row'
   for row in soup.find_all("div", {"class": "views-row"}):
       # Find the download URL and the PLS URL
       download_url = row.find("a", {"class": "plsr-download-link plsr-link"})["href"]
       pls_url = row.find("h5", {"class": "field-content"}).find("a")["href"]
       # Append the download URL and the PLS URL to their respective lists
       download_urls.append(download_url)
       pls_urls.append(pls_url)
       # Send a GET request to the PLS URL
       reqs2 = requests.get(main_url + pls_url)
       # Parse the response text with BeautifulSoup
       soup2 = BeautifulSoup(reqs2.text, 'html.parser')
       # Find the NCT ID
       nct = soup2.find("div", {"class": "plsr-nct-id plsr-row"}).find("a")['href']
       # Open the file in append mode and write the download URL, the PLS URL, and the NCT ID to it
       with open("links_documents_pfizer.txt", "a", encoding='utf-8') as f:
           f.write(f"{main_url + download_url};{main_url + pls_url};{nct}\n")

# Read the file 'links_documents_pfizer.txt' and download the PDFs
with open('links_documents_pfizer.txt', 'r', encoding='utf-8') as f:
   for line in f:
       # Split the line into three parts
       parts = line.split(';')
       # Send a GET request to the download URL
       reqs3 = requests.get(parts[0])
       # Open the file in write mode and write the response content to it
       with open(f"pfizer_documents/{parts[2]}.pdf", "wb") as f2:
           f2.write(reqs3.content)
