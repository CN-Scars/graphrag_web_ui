<div align="center">
    English | <a href="README_ZH-CN.md">简体中文</a>
</div>


# 📚 GraphRAG Web UI

GraphRAG Web UI is a local knowledge base management and Q&A system based on Streamlit. It allows users to create, manage, delete, and query the knowledge base through an easy-to-use web interface.

## 🚀 Project Overview

GraphRAG Web UI is built using Microsoft's open-source library [GraphRAG](https://github.com/microsoft/graphrag). Through a web interface developed with Streamlit, users can easily initialize, index, and query the knowledge base, creating a simple knowledge base Q&A system. This project aims to simplify the process of maintaining and querying a knowledge base, offering the following core features.

## ✨ Features

- **Knowledge Base Management**: Create, delete, and list existing knowledge bases.
- **Configuration Editing**: Edit the `.env` and `settings.yaml` configuration files through the web interface.
- **File Management**: Upload and delete knowledge files (`.txt` files).
- **Knowledge Base Initialization and Indexing**: Initialize and index the knowledge base using `GraphRAG` commands.
- **Q&A Module**: Query the knowledge base with support for various query methods (local, global, drift).

## 🔧 System Requirements

- 🐍 **Python 3.11**
- 🚀 **Streamlit 1.27.0** or newer
- ⚙️ **GraphRAG 0.4.0** or newer
- 📦 Dependencies specified in `requirements.txt`

## 💻 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/CN-Scars/graphrag_web_ui
cd graphrag_web_ui
```

### 2. Create and Activate a Virtual Environment

Using `venv`:

```bash
python3 -m venv graph_rag
source graph_rag/bin/activate  # Unix/Linux
graph_rag\Scripts\activate     # Windows
```

Or using Anaconda:

```bash
conda create -n graph_rag python=3.11
conda activate graph_rag
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 📦 Usage

Launch the Streamlit app:

```bash
streamlit run app-en.py
```

Open your browser and visit [http://localhost:8501](http://localhost:8501/) to use the GraphRAG Web UI.

## 📝 Notes

- 🔧 Before using the indexing feature, ensure that [GraphRAG](https://github.com/microsoft/graphrag) is properly installed and configured.
- 📝 The `.env` and `settings.yaml` files can be manually modified or edited through the provided UI.
- 📂 Knowledge bases are stored in the `knowledge_bases/` directory.
- 📁 Uploaded files are temporarily stored in the `uploads/` directory.

## 🤝 Contributions

Issues and pull requests are welcome to help improve this project.

## 📝 License

[MIT](https://github.com/CN-Scars/graphrag_web_ui/blob/main/LICENSE)

------

If you have any questions, feel free to reach out!

<div align="center">
    <p><strong>GraphRAG Web UI</strong></p> English | <a href="README_ZH-CN.md">简体中文</a>
</div>
