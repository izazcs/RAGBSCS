from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / 'BCComputerScienceCoursecontent.pdf'
CHROMA_DIR = BASE_DIR / 'chroma_db'
print('PDF exists:', PDF_PATH.exists())
loader = PyPDFLoader(str(PDF_PATH))
pages = loader.load()
print('Pages loaded:', len(pages))

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150, separators=['\n\n','\n','.',' '])
chunks = splitter.split_documents(pages)
print('Chunks created:', len(chunks))
for i, chunk in enumerate(chunks[:5], 1):
    print('--- chunk', i, 'len', len(chunk.page_content), 'source', chunk.metadata.get('source'), 'chunk_index', chunk.metadata.get('chunk_index'))
    print(chunk.page_content[:200].replace('\n',' '))

term = 'Operating system'
matched = [i for i, chunk in enumerate(chunks) if term.lower() in chunk.page_content.lower()]
print('Chunks matching term:', len(matched), matched[:20])

if CHROMA_DIR.exists():
    try:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        db = Chroma(collection_name='course_content', embedding_function=embeddings, persist_directory=str(CHROMA_DIR))
        print('Chroma collection count available:', getattr(db, '_collection_count', 'no attr'))
        try:
            ids = db._collection.get()['ids']
            print('Vector count by ids:', len(ids))
        except Exception as e:
            print('Could not get ids from _collection:', e)
    except Exception as e:
        print('Chroma inspect error:', e)
else:
    print('No chroma dir')
