import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from docx import Document
import magic
from datetime import datetime
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.fake import FakeListLLM

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# In-memory document store
documents = []

# Helper functions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_type = magic.from_file(file_path, mime=True)
        if file_type == 'application/pdf':
            text = extract_text_from_pdf(file_path)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text = extract_text_from_docx(file_path)
        elif file_type == 'text/plain':
            text = extract_text_from_txt(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        documents.append({'filename': filename, 'text': text})
        return jsonify({'message': 'File uploaded and processed successfully', 'filename': filename})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = data.get('query')
    if not query_text:
        return jsonify({'error': 'No query provided'}), 400
    if not documents:
        return jsonify({'error': 'No documents uploaded yet.'}), 400
    # Combine all docs for demo; in production, use per-doc QA
    all_text = '\n'.join([doc['text'] for doc in documents])
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_text(all_text)
    # Use fake embeddings and LLM for demo; replace with real ones for production
    embeddings = FakeEmbeddings(size=32)
    vectordb = FAISS.from_texts(texts, embeddings)
    retriever = vectordb.as_retriever()
    llm = FakeListLLM(responses=[f"Pretend answer for: {query_text}"])
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    answer = qa.run(query_text)
    return jsonify({'results': [answer]})

@app.route('/documents', methods=['GET'])
def list_documents():
    return jsonify({'documents': [{'source': doc['filename']} for doc in documents]})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True) 