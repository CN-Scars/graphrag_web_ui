import streamlit as st
import os
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv
import yaml
import pkg_resources
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check Streamlit version and select the appropriate rerun method
try:
    st_version = pkg_resources.parse_version(st.__version__)
    required_version = pkg_resources.parse_version(
        "1.27.0")  # Minimum required version: 1.27.0
    if st_version >= required_version:
        rerun_method = st.rerun
    else:
        raise AttributeError
except AttributeError:
    rerun_method = st.experimental_rerun
    st.warning("Your Streamlit version is outdated. Please upgrade to version 1.27.0 or later to support the refresh feature.")

# Configure the page
st.set_page_config(page_title="GraphRAG Web UI", layout="wide")

# Root directories
ROOT_DIR = Path(__file__).parent.resolve()
KB_DIR = ROOT_DIR / "knowledge_bases"
UPLOAD_DIR = ROOT_DIR / "uploads"

# Ensure required directories exist
KB_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


def list_knowledge_bases():
    """List all knowledge bases"""
    return [d.name for d in KB_DIR.iterdir() if d.is_dir()]


def create_knowledge_base(name):
    """Create and initialize a new knowledge base"""
    kb_path = KB_DIR / name
    input_path = kb_path / "input"
    kb_path.mkdir(parents=True, exist_ok=True)
    input_path.mkdir(parents=True, exist_ok=True)

    # Execute initialization command with a loading spinner
    with st.spinner("Initializing knowledge base..."):
        output = run_graphrag_command(
            ["init", "--root", str(kb_path)], cwd=ROOT_DIR)

    # Output initialization result to the console
    print(f"Initialization output for {name}: {output}")

    # Check if initialization was successful
    expected_message = f"Initializing project at {kb_path}"
    if expected_message in output:
        return (True, "Knowledge base successfully created and initialized!")
    else:
        return (False, "Initialization failed. Please check if GraphRAG is installed and configured correctly.")


def delete_knowledge_base(name):
    """Delete a specified knowledge base"""
    kb_path = KB_DIR / name
    if kb_path.exists() and kb_path.is_dir():
        shutil.rmtree(kb_path)
        return (True, f"Knowledge base '{name}' has been deleted!")
    else:
        return (False, f"Knowledge base '{name}' does not exist!")


def clear_cache(kb_path):
    """Clear cache files and folders in the specified knowledge base, retaining input, prompts, .env, and settings.yaml"""
    exclusions = {"input", "prompts", ".env", "settings.yaml"}
    for item in kb_path.iterdir():
        if item.name in exclusions:
            logger.info(f"Retained file or folder: {item}")
            continue
        try:
            if item.is_dir():
                shutil.rmtree(item)
                logger.info(f"Deleted directory: {item}")
            else:
                item.unlink()
                logger.info(f"Deleted file: {item}")
        except Exception as e:
            logger.error(f"Error deleting {item}: {e}")
            st.error(f"Error deleting {item}: {e}")


def edit_env(kb_path):
    """Edit the .env file"""
    env_path = kb_path / ".env"
    load_dotenv(dotenv_path=env_path)
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                env_content = f.read()
        except Exception as e:
            st.error(f"Error reading .env file: {e}")
            env_content = ""
    else:
        env_content = ""
    st.subheader(".env File Editor")
    new_env = st.text_area("Edit .env file content", env_content, height=200)
    if st.button("Save .env file"):
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(new_env)
            st.success(".env file saved!")
            rerun_method()  # Automatically refresh the page
        except Exception as e:
            st.error(f"Error saving .env file: {e}")


def edit_settings(kb_path):
    """Edit the settings.yaml file"""
    settings_path = kb_path / "settings.yaml"
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_content = f.read()
        except Exception as e:
            st.error(f"Error reading settings.yaml file: {e}")
            settings_content = ""
    else:
        settings_content = ""
    st.subheader("settings.yaml File Editor")
    new_settings = st.text_area(
        "Edit settings.yaml file content", settings_content, height=600)
    if st.button("Save settings.yaml file"):
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(new_settings)
            st.success("settings.yaml file saved!")
            rerun_method()  # Automatically refresh the page
        except Exception as e:
            st.error(f"Error saving settings.yaml file: {e}")


def manage_files(kb_path):
    """Manage .txt files in the knowledge base"""
    input_path = kb_path / "input"
    st.subheader("Manage Knowledge Files (TXT files in input folder)")
    # List existing files
    files = [f.name for f in input_path.glob("*.txt")]
    st.write("Existing files:")
    if files:
        for file in files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(file)
            with col2:
                if st.button(f"Delete {file}", key=f"del_{file}"):
                    try:
                        os.remove(input_path / file)
                        st.success(f"File '{file}' deleted!")
                        print(f"File '{file}' deleted!")
                        rerun_method()  # Automatically refresh the page
                    except Exception as e:
                        st.error(f"Error deleting file '{file}': {e}")
    else:
        st.info("No uploaded TXT files.")
    st.write("---")
    # Upload files
    uploaded_files = st.file_uploader(
        "Upload new TXT files", type=["txt"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_path = input_path / uploaded_file.name
            try:
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                print(f"File '{uploaded_file.name}' uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading file '{uploaded_file.name}': {e}")
        st.success(f"Uploaded {len(uploaded_files)} files.")
        rerun_method()  # Automatically refresh the page


def run_graphrag_command(args, cwd):
    """Call GraphRAG commands via subprocess and output results to the console"""
    try:
        result = subprocess.run(
            ["python", "-m", "graphrag"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout
            text=True,
            check=True
        )
        print(f"Command Output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command Error: {e.output}")
        return f"Error: {e.output}"


def parse_graphrag_response(output, method):
    """Parse the response from GraphRAG commands"""
    markers = {
        "local": "SUCCESS: Local Search Response:",
        "global": "SUCCESS: Global Search Response:",
        "drift": "SUCCESS: DRIFT Search Response:"
    }
    marker = markers.get(method.lower())
    if not marker:
        return None
    start = output.find(marker)
    if start == -1:
        return None
    return output[start + len(marker):].strip()


def index_knowledge_base(name):
    """Index the specified knowledge base"""
    kb_path = KB_DIR / name

    # Execute indexing command with a loading spinner
    with st.spinner("Indexing knowledge base..."):
        output = run_graphrag_command(
            ["index", "--root", str(kb_path)], cwd=ROOT_DIR)

    # Output indexing result to the console
    print(f"Indexing output for {name}: {output}")

    # Check if indexing was successful
    expected_message = "All workflows completed successfully."
    if expected_message in output:
        st.success("Knowledge base indexed successfully!")
        logger.info(f"Knowledge base '{name}' indexed successfully!")
        rerun_method()  # Automatically refresh the page to display the latest content
    else:
        st.error(
            "Indexing failed. Please check if GraphRAG is installed and configured correctly.")


# Main UI
st.title("GraphRAG Web UI")

menu = ["Knowledge Base Management", "Knowledge Base Q&A"]
choice = st.sidebar.selectbox("Select Module", menu)

if choice == "Knowledge Base Management":
    st.header("Knowledge Base Management")
    kb_list = list_knowledge_bases()

    col1, col2 = st.columns(2)
    with col1:
        new_kb = st.text_input("New Knowledge Base Name")
        if st.button("Add Knowledge Base"):
            if new_kb:
                if new_kb in kb_list:
                    st.error("Knowledge base name already exists!")
                else:
                    success, message = create_knowledge_base(new_kb)
                    if success:
                        st.success(message)
                        rerun_method()  # Automatically refresh the page
                    else:
                        st.error(message)
            else:
                st.error("Please enter a knowledge base name!")
    with col2:
        if kb_list:
            del_kb = st.selectbox("Select a Knowledge Base to Delete", [
                                  ""] + kb_list, index=0)
            if st.button("Delete Knowledge Base"):
                if del_kb and del_kb in kb_list:
                    success, message = delete_knowledge_base(del_kb)
                    if success:
                        st.success(message)
                        rerun_method()  # Automatically refresh the page
                    else:
                        st.error(message)
                else:
                    st.error("Please select a knowledge base to delete!")
        else:
            st.info("No knowledge bases available to delete.")

    # Add a Refresh button next to "Existing Knowledge Bases List"
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("Existing Knowledge Bases List")
    with col2:
        if st.button("Refresh List"):
            rerun_method()  # Manually trigger page rerun

    # List knowledge bases
    if kb_list:
        for kb in kb_list:
            st.write(f"- {kb}")
    else:
        st.info("No knowledge bases currently available.")

    st.write("---")

    # Select a knowledge base to manage
    if kb_list:
        selected_kb = st.selectbox(
            "Select a Knowledge Base to Manage", kb_list, key="manage_select")
        if selected_kb:
            kb_path = KB_DIR / selected_kb
            st.write(f"Currently managing: **{selected_kb}**")
            tab1, tab2, tab3, tab4 = st.tabs(
                ["Edit .env", "Edit settings.yaml", "Manage Knowledge Files", "Index Knowledge Base"])

            with tab1:
                edit_env(kb_path)

            with tab2:
                edit_settings(kb_path)

            with tab3:
                manage_files(kb_path)

            with tab4:
                st.subheader("Index Knowledge Base")
                st.write(
                    "Click the button below to index the knowledge base using GraphRAG.")

                # Add a checkbox for clearing the cache
                clear_cache_option = st.checkbox("Clear Cache")

                if st.button("Index Knowledge Base", key=f"index_{selected_kb}"):
                    if clear_cache_option:
                        with st.spinner("Clearing cache..."):
                            clear_cache(kb_path)
                        st.success("Cache cleared!")

                    index_knowledge_base(selected_kb)
    else:
        st.info("No knowledge bases currently available for management.")

elif choice == "Knowledge Base Q&A":
    st.header("Knowledge Base Q&A")
    kb_list = list_knowledge_bases()
    if not kb_list:
        st.error("No knowledge bases available. Please create one first.")
    else:
        selected_kb = st.selectbox(
            "Select a Knowledge Base to Query", kb_list, key="qa_select")
        if selected_kb:
            kb_path = KB_DIR / selected_kb
            query = st.text_input("Enter your question")
            method = st.selectbox("Select Query Method", [
                                  "local", "global", "drift"])
            if st.button("Submit Query"):
                if query:
                    with st.spinner("Processing your question, please wait..."):
                        # Execute query
                        args = ["query", "--root",
                                str(kb_path), "--method", method, "--query", query]
                        output = run_graphrag_command(args, cwd=ROOT_DIR)
                        # Parse response
                        response = parse_graphrag_response(output, method)
                    print(f"Query output for {selected_kb}: {output}")
                    if response:
                        st.markdown(response)
                    else:
                        st.error(
                            "No valid response found. The knowledge base might not be initialized or there might be other errors.")
                else:
                    st.error("Please enter your question!")
