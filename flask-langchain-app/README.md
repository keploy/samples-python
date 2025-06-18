# Flask Document Chatbot

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/your-repo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern web application that allows users to upload documents (PDF, DOCX, TXT) and ask questions about their content using ChromaDB for document storage and retrieval. Powered by Flask, LangChain, and FAISS.

---

## 🚀 Quick Start

### Run with Docker (Recommended)
```bash
git clone <repository-url>
cd flask-chromadb-app
docker-compose up --build
```
Visit: [http://localhost:5001](http://localhost:5001)

### Run Locally (Python)
```bash
git clone <repository-url>
cd flask-chromadb-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Visit: [http://localhost:5000](http://localhost:5000)

---

## ✨ Features
- Modern, responsive UI with smooth animations
- Drag-and-drop file upload
- Support for PDF, DOCX, and TXT files
- Real-time chat interface
- Document management system
- Semantic search using ChromaDB & FAISS
- Beautiful loading animations and transitions

---

## 🖼️ Demo
<!--
Add a screenshot or GIF of the app below. Example:
![Demo Screenshot](static/demo-screenshot.png)
-->

---

## 📦 Project Structure
```
flask-chromadb-app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker build file
├── docker-compose.yml  # Docker Compose config
├── .dockerignore       # Docker ignore file
├── static/
│   ├── css/
│   │   └── style.css  # Custom styles
│   ├── js/
│   │   └── main.js    # Frontend JavaScript
│   └── uploads/       # Uploaded documents
├── templates/
│   └── index.html     # Main template
└── db/                # ChromaDB storage
```

---

## ⚙️ Configuration & Customization
- **UI Customization:** Edit `static/css/style.css` and `templates/index.html` for branding and layout changes.
- **File Size Limit:** Adjust `MAX_CONTENT_LENGTH` in `app.py`.
- **Allowed File Types:** Update `ALLOWED_EXTENSIONS` in `app.py`.

---

## 📝 Usage
1. **Upload** a document by dragging and dropping it or clicking "Browse Files".
2. **Wait** for the document to be processed (progress bar will show).
3. **Ask** a question in the chat input field.
4. **View** the chatbot's answer based on your document content.

**Example Q&A:**
- Q: "What is the main topic of this document?"
- Q: "Summarize the second section."
- Q: "List all dates mentioned."

---

## 🛠️ Dependencies
- `flask`
- `langchain`
- `langchain-community`
- `faiss-cpu`
- `numpy==1.26.4` (required for FAISS compatibility)
- `python-docx`, `pymupdf`, `python-magic`, etc.

---

## 🐳 Docker Notes
- The app runs on port **5001** by default (see `docker-compose.yml`).
- Uploaded files and ChromaDB data persist in `static/uploads` and `db`.
- To stop the app: `Ctrl+C` then `docker-compose down`.

---

## ❓ FAQ & Troubleshooting

**Q: I get `ModuleNotFoundError: No module named 'numpy.distutils'` or FAISS import errors.**
- A: Ensure your `requirements.txt` includes:
  ```
  numpy==1.26.4
  faiss-cpu
  ```
  Then rebuild Docker: `docker-compose build && docker-compose up`

**Q: Port 5000 is already in use!**
- A: The Docker app is mapped to port **5001**. Visit [http://localhost:5001](http://localhost:5001)

**Q: How do I change the upload size or allowed file types?**
- A: Edit `MAX_CONTENT_LENGTH` and `ALLOWED_EXTENSIONS` in `app.py`.

---

## 🤝 Contributing
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📬 Contact & Support
For questions, issues, or feature requests, please open an issue on GitHub or contact the maintainer at [your-email@example.com]. 