# 📄 AI Document Analyzer

An AI-powered document analysis application built with **Python, Streamlit, Groq LLM, and RAG (Retrieval-Augmented Generation)**.

The application allows users to upload different types of documents and interact with their content using AI. It can summarize documents, answer questions, extract important information, generate quizzes, and produce structured insights.

---

## 🚀 Features

### 📤 Document Upload

Upload and analyze:

* 📕 PDF
* 📝 DOCX
* 📄 TXT
* 📊 CSV

### 🤖 AI-Powered Analysis

The application provides several document analysis features:

* 📝 **Summarize Document**
* 🔍 **Ask Questions**
* 🔑 **Extract Keywords**
* 📌 **Extract Important Points**
* 📊 **Extract Structured Data**
* 🧠 **Generate Quiz**
* 📑 **Generate Report**

### 💬 Question Answering with RAG

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant sections of the uploaded document before sending the context to the LLM.

This helps the AI provide answers based on the uploaded document rather than relying only on general knowledge.

---

## 🏗️ Project Architecture

```text
AI Document Analyzer
│
├── 📤 Upload Document
│
├── 📚 Document Processing
│   ├── PDF
│   ├── DOCX
│   ├── TXT
│   └── CSV
│
├── ✂️ Text Chunking
│
├── 🔢 Embeddings / Vector Store
│
├── 🔍 Relevant Context Retrieval
│
├── 🤖 Groq LLM
│
└── 📊 Document Analysis
    ├── Summarization
    ├── Question Answering
    ├── Keyword Extraction
    ├── Important Points
    ├── Structured Data
    ├── Quiz Generation
    └── Report Generation
```

---

## 🛠️ Technologies Used

| Technology       | Purpose                           |
| ---------------- | --------------------------------- |
| 🐍 Python        | Application development           |
| 🎨 Streamlit     | Web application UI                |
| ⚡ Groq API       | Large Language Model inference    |
| 🧠 RAG           | Document-based question answering |
| 🔢 Vector Store  | Semantic document retrieval       |
| 📄 PyPDF         | PDF processing                    |
| 📝 python-docx   | DOCX processing                   |
| 📊 Pandas        | CSV/data processing               |
| 🔐 python-dotenv | Environment variable management   |

---

## 📁 Project Structure

```text
ai_document_analyzer/
│
├── app.py
│
├── config.py
│
├── requirements.txt
│
├── .gitignore
│
├── README.md
│
└── modules/
    │
    ├── __init__.py
    ├── analyzer.py
    ├── document_loader.py
    ├── embeddings.py
    ├── llm.py
    ├── prompts.py
    └── vector_store.py
```

> The exact module names may vary depending on your current project structure.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/ai-document-analyzer.git
```

Move into the project directory:

```bash
cd ai-document-analyzer
```

---

### 2. Create a Virtual Environment

For Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

You should see:

```text
(venv)
```

before your command prompt.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Configuration

This project uses the **Groq API** for AI-powered document analysis.

Create an API key from the Groq Console and store it securely as an environment variable.

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### ⚠️ Important

**Never upload your API key to GitHub.**

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
venv/
.venv/
```

---

## ▶️ Run the Application

After activating the virtual environment and installing the dependencies, run:

```bash
streamlit run app.py
```

The application will open in your browser.

Usually Streamlit runs at:

```text
http://localhost:8501
```

---

## 🧠 How RAG Works in This Project

The application follows a Retrieval-Augmented Generation workflow.

```text
User uploads document
        ↓
Document text extraction
        ↓
Text cleaning
        ↓
Text chunking
        ↓
Create embeddings
        ↓
Store document vectors
        ↓
User asks a question
        ↓
Retrieve relevant chunks
        ↓
Build context
        ↓
Send context + question to Groq LLM
        ↓
Generate answer
        ↓
Display answer in Streamlit
```

### Why RAG?

Traditional LLM applications may answer using only the model's existing knowledge.

With RAG, the application first retrieves relevant information from the uploaded document and provides that information to the LLM.

This makes the system more suitable for:

* 📄 Resume analysis
* 📚 Research papers
* 📑 Business reports
* 🏥 Documents and records
* 📋 Company documents
* 📖 Study materials
* 📊 Data reports

---

## 💡 Example Use Case

Suppose a user uploads a resume.

They can ask:

```text
What are the strongest technical skills mentioned in this resume?
```

The system:

1. Reads the uploaded resume.
2. Splits the document into chunks.
3. Retrieves the relevant sections.
4. Sends the relevant context to the Groq LLM.
5. Generates an answer based on the resume.

Example output:

```text
The strongest technical skills include:

• Python
• SQL
• Machine Learning
• Power BI
• Advanced Excel
```

---

## 🎯 Main Application Features

### 📝 Summarization

Generate a concise summary of the uploaded document.

### 🔍 Ask Questions

Ask natural-language questions about the document.

Example:

```text
What are the key findings of this report?
```

### 🔑 Keyword Extraction

Identify important keywords and concepts.

### 📌 Important Points

Extract the most important information from the document.

### 📊 Structured Data Extraction

Convert relevant document information into a structured format.

### 🧠 Quiz Generation

Generate questions from the uploaded document for learning and assessment.

### 📑 Report Generation

Generate an organized report based on the document contents.

---

## 🔒 Security

Sensitive information should never be committed to GitHub.

The following files should remain private:

```text
.env
API keys
Passwords
Credentials
Private documents
```

Use environment variables for API credentials.

---

## ☁️ Deployment

The application can be deployed using **Streamlit Community Cloud**.

Basic deployment process:

```text
GitHub Repository
       ↓
Connect Repository to Streamlit
       ↓
Select app.py
       ↓
Configure Secrets
       ↓
Deploy
       ↓
Live Streamlit Application
```

For deployment, add your API key through Streamlit's **Secrets** configuration rather than uploading `.env` to GitHub.

Example secret:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

---

## 📌 Future Improvements

Possible future enhancements include:

* 🔐 User authentication
* 💾 Conversation history
* 📚 Multiple-document RAG
* 🔎 Advanced semantic search
* 📊 More structured data extraction
* 📈 Document analytics dashboard
* 🗂️ Document history
* 🧠 Improved embedding models
* 💬 Chat history and memory
* 📥 Export AI-generated reports
* 🌐 Multi-language document analysis
* 📷 OCR support for scanned documents

---

## 🎓 Learning Outcomes

This project demonstrates practical experience with:

* Python application development
* Streamlit
* LLM integration
* Groq API
* Prompt engineering
* RAG architecture
* Document processing
* Text chunking
* Vector search
* Embeddings
* AI-powered question answering
* API integration
* Environment variable management
* Git and GitHub
* Cloud deployment

---

## 📸 Application

### Upload Document

```text
📄 AI Document Analyzer

Upload your document
[ Choose a file ]

Supported formats:
PDF | DOCX | TXT | CSV
```

### Analyze Document

```text
Select an action:

📝 Summarize
🔍 Ask Questions
🔑 Extract Keywords
📌 Important Points
📊 Structured Data
🧠 Generate Quiz
📑 Generate Report
```

---

## 👨‍💻 Author

**Shreyasree Mete**

MCA Graduate | Python | AI/ML | Data Analytics | Generative AI

---

## ⭐ If You Like This Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.
