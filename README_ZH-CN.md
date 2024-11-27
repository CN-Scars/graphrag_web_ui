<div align="center">
    <a href="README.md">English</a> | 简体中文
</div>


# 📚 GraphRAG Web UI

GraphRAG Web UI 是一个基于 Streamlit 的本地知识库管理与问答系统。它允许用户通过简单易用的 Web 界面来创建、管理、删除和查询知识库。

## 🚀 项目简介

GraphRAG Web UI 利用微软的开源库 [GraphRAG](https://github.com/microsoft/graphrag) 构建而成。通过 Streamlit 搭建的 Web 界面，用户可以方便地对知识库进行初始化、索引和查询，从而实现一个简易的知识库问答系统。这个项目旨在简化维护和查询知识库的过程，主要功能如下。

## ✨ 功能特性

- **知识库管理**：创建、删除和列出现有的知识库。
- **配置编辑**：通过 Web 界面编辑 `.env` 和 `settings.yaml` 配置文件。
- **文件管理**：上传和删除知识文件（`.txt` 文件）。
- **知识库初始化和索引**：使用 `GraphRAG` 命令对知识库进行初始化和索引。
- **问答模块**：对知识库进行查询，支持多种查询方法（local、global、drift）。

## 🔧 系统要求

- 🐍 **Python 3.11**
- 🚀 **Streamlit 1.27.0** 或更新版本
- ⚙️ **GrahRAG 0.4.0** 或更新版本
- 📦 `requirements.txt` 中指定的依赖项

## 💻 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/CN-Scars/graphrag_web_ui
cd graphrag_web_ui
```

### 2. 创建并激活虚拟环境

使用 `venv`：

```bash
python3 -m venv graph_rag
source graph_rag/bin/activate  # Unix/Linux
graph_rag\Scripts\activate     # Windows
```

或者使用 Anaconda：

```bash
conda create -n graph_rag python=3.11
conda activate graph_rag
```

### 3. 安装依赖项

```bash
pip install -r requirements.txt
```

## 📦 使用方法

启动 Streamlit 应用：

```bash
streamlit run app-cn.py
```

打开浏览器访问 [http://localhost:8501](http://localhost:8501/)，即可使用 GraphRAG Web UI。

## 📝 注意事项

- 🔧 在使用索引功能之前，请确保 [GraphRAG](https://github.com/microsoft/graphrag) 已正确安装和配置。
- 📝 `.env` 和 `settings.yaml` 文件可以手动修改或通过提供的 UI 编辑。
- 📂 知识库存储在 `knowledge_bases/` 目录中。
- 📁 上传的文件临时存放在 `uploads/` 目录中。

## 🤝 贡献

欢迎提交问题和拉取请求以帮助改进该项目。

## 📝 许可证

[MIT](https://github.com/CN-Scars/graphrag_web_ui/blob/main/LICENSE)

------

如果您有任何问题，欢迎随时联系！

<div align="center">
    <p><strong>GraphRAG Web UI</strong></p> <a href="README.md">English</a> | 简体中文
</div>