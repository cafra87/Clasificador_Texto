import re
import os

# Get a list of all files in the 'full_texts' directory
texts = os.listdir('full_texts')

# Loop through each file
for text in texts:
   # Construct the full path to the input file
   input_file_path = f"full_texts/{text}"
   print(text)

   # Read the input text from the file
   with open(input_file_path, "r", encoding="utf-8") as file:
       input_text = file.read()

   # Define the regular expression pattern with the re.IGNORECASE flag
   # This pattern matches the text between "What happened during the study?" and "What were the results of the study?"
   pattern = r"(?i)What happened during the study\?(.*?)What were the results of the study\?"

   # Find all matches using re.findall and re.IGNORECASE
   matches = re.findall(pattern, input_text, re.IGNORECASE | re.DOTALL)

   # Extracted text
   extracted_text = matches[0].strip() if matches else ""

   # Create a dictionary to store the extracted text
   json_data = {"extracted_text": extracted_text}

   # Define the path to the output JSON file
   # The output file name is the same as the input file name, but without the extension
   name = text.split('.')[0]
   output_file_path = f"fragment/{name}"

   # Write the extracted text to the output file
   with open(f"{output_file_path}.txt", "w", encoding="utf-8") as file:
       file.write(extracted_text)

   print(f"Text extracted and saved to '{output_file_path}'")
