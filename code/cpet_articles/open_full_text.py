from pathlib import Path
import subprocess

def check_quit(test, check = 'q'):
    if test == check:
        print("Quitting program\n")
        quit()

def open_full_text_file():
    # opens a full-text file in the order of pdf, epub, then txt
    file_name = str(input('Enter the file name (DOI suffix) of the file you wish to open, or enter "q" to quit: '))
    check_quit(file_name)

    full_text_folder_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/full_texts')

    full_text_file_extensions = ['pdf', 'epub', 'txt']

    for file_ext in full_text_file_extensions:
        file_path = Path(full_text_folder_path / (file_ext + 's') / (file_name + '.' + file_ext))
        if file_ext == 'pdf':
            cmd = f'open -a "Adobe Acrobat" "{file_path}"'
        else:
            cmd = f'open "{file_path}"'

        run = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        try:
            out, err = run.communicate(timeout=5)
            if err:
                continue
            else:
                open_full_text_file()
        except Exception as e:
            run.kill()
            out, err = run.communicate()
            if err:
                continue
    # If it gets to this point, the file can't be found.
    print(f'{file_name} not found\n')
    open_full_text_file()

if __name__ == "__main__":
    open_full_text_file()