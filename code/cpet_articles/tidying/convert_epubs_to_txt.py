from pathlib import Path
from epub2txt import epub2txt

proj_folder_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review')
epub_folder = proj_folder_path / 'data' / 'cpet_articles' / 'full_texts' / 'epubs'
epub_paths = list(epub_folder.glob('*.epub'))
path = epub_paths[12]
txt_folder = proj_folder_path / 'data' / 'cpet_articles' / 'full_texts' # / 'txts'
for path in epub_paths:
    res = epub2txt(path)
    fname = str(txt_folder / (path.stem + '.txt'))
    with open(fname, 'w') as f:
        f.write(res)

# txt_folder = proj_folder_path / 'data' / 'cpet_articles' / 'full_texts'
# fname = str(txt_folder / (path.stem + '.txt'))
# with open(fname, 'w') as f:
#     f.write(res)


# res = epub2txt(epub_paths[0])
# res

# book = epub.read_epub(epub_paths[22])
# book

# list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

# text = []
# for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
#     text.append(str(doc.content))

# text = sum(text)
# text[0]