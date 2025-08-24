import os

def get_paragraphs(input_filename):
    with open(input_filename, 'r', encoding='utf-8') as input_file:
        content = input_file.read()
        paragraphs = content.split('\n')
        if paragraphs[-1] == '':
            paragraphs = paragraphs[:-1]
        text = ''

        for i, paragraph in enumerate(paragraphs):
            if paragraph == '':
                continue
            words = paragraph.split()
            len_text_ant = len(text.split())
            text = text + paragraph + '\n'
            len_text = len(text.split())
            if len(words) > 250:
                print(f'Saving paragraph {i+1}...')
                output_filename = f'{input_filename}_section{i+1}.txt'
                with open(output_filename, 'w', encoding='utf-8') as output_file:
                    output_file.write(paragraph)
            if len_text - len_text_ant > 50 and len_text > 250 and i != len(paragraphs) - 1:
                print(f'Saving accumulated paragraphs {i+1}...')
                output_filename = f'{input_filename}_accumulated_section{i+1}.txt'
                with open(output_filename, 'w', encoding='utf-8') as output_file:
                    output_file.write(text)
    print("Process completed for the file: " + input_filename)

input_folder = 'clinical_trials_no_plain'
for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_folder, filename)
        get_paragraphs(file_path)
        
input_folder = 'clinical_trials_no_plain'
for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_folder, filename)
        get_paragraphs(file_path)



