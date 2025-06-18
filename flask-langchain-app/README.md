# Flask Document Chatbot

A modern web application that allows users to upload documents (PDF, DOCX, TXT) and ask questions about their content using ChromaDB for document storage and retrieval.

## Features

- Modern, responsive UI with smooth animations
- Drag-and-drop file upload
- Support for PDF, DOCX, and TXT files
- Real-time chat interface
- Document management system
- Semantic search using ChromaDB
- Beautiful loading animations and transitions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation (Local)

1. Clone the repository:
```bash
git clone <repository-url>
cd flask-chromadb-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application (Local)

1. Make sure your virtual environment is activated
2. Run the Flask application:
```bash
python app.py
```
3. Open your web browser and navigate to `http://localhost:5000`

## Running with Docker (Recommended)

1. Build and start the app using Docker Compose:
```bash
cd flask-chromadb-app
docker-compose up --build
```
2. Open your browser and go to `http://localhost:5000`

- Uploaded files and ChromaDB data will persist in the `static/uploads` and `db` folders.
- To stop the app, press `Ctrl+C` and run `docker-compose down`.

## Usage

1. Upload a document by dragging and dropping it into the upload zone or clicking the "Browse Files" button
2. Wait for the document to be processed
3. Type your question in the chat input field
4. View the response from the chatbot

## Project Structure

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

## Technologies Used

- Flask: Web framework
- ChromaDB: Vector database for document storage and retrieval
- TailwindCSS: Utility-first CSS framework
- Animate.css: Animation library
- JavaScript: Frontend interactivity
- Docker: Containerization

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 