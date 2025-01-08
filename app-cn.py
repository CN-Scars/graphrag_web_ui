import streamlit as st
import os
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv
import yaml
import pkg_resources
import logging


# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 检查 Streamlit 版本并选择适当的 rerun 方法
try:
    st_version = pkg_resources.parse_version(st.__version__)
    required_version = pkg_resources.parse_version("1.27.0")  # 将最低版本调整为1.27.0
    if st_version >= required_version:
        rerun_method = st.rerun
    else:
        raise AttributeError
except AttributeError:
    rerun_method = st.experimental_rerun
    st.warning("你的 Streamlit 版本较旧，建议升级至 1.27.0 及以上以支持刷新功能。")

# 配置页面
st.set_page_config(page_title="GraphRAG Web UI", layout="wide")

# 根目录
ROOT_DIR = Path(__file__).parent.resolve()
KB_DIR = ROOT_DIR / "knowledge_bases"
UPLOAD_DIR = ROOT_DIR / "uploads"

# 确保目录存在
KB_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


def list_knowledge_bases():
    """列出所有知识库"""
    return [d.name for d in KB_DIR.iterdir() if d.is_dir()]


def create_knowledge_base(name):
    """创建新的知识库并初始化"""
    kb_path = KB_DIR / name
    input_path = kb_path / "input"
    kb_path.mkdir(parents=True, exist_ok=True)
    input_path.mkdir(parents=True, exist_ok=True)

    # 执行初始化命令，并使用 spinner 显示加载动画
    with st.spinner("正在初始化知识库..."):
        output = run_graphrag_command(
            ["init", "--root", str(kb_path)], cwd=ROOT_DIR)

    # 输出初始化结果到控制台
    print(f"初始化输出 for {name}: {output}")

    # 判断初始化是否成功
    expected_message = f"Initializing project at {kb_path}"
    if expected_message in output:
        return (True, "知识库创建并初始化成功！")
    else:
        return (False, "初始化失败，请检查 graphrag 是否正确安装或配置。")


def delete_knowledge_base(name):
    """删除指定的知识库"""
    kb_path = KB_DIR / name
    if kb_path.exists() and kb_path.is_dir():
        shutil.rmtree(kb_path)
        return (True, f"知识库 '{name}' 已删除！")
    else:
        return (False, f"知识库 '{name}' 不存在！")


def clear_cache(kb_path):
    """清除指定知识库的缓存文件和文件夹，保留 input、prompts、.env 和 settings.yaml"""
    exclusions = {"input", "prompts", ".env", "settings.yaml"}
    for item in kb_path.iterdir():
        if item.name in exclusions:
            logger.info(f"保留文件或文件夹: {item}")
            continue
        try:
            if item.is_dir():
                shutil.rmtree(item)
                logger.info(f"已删除目录: {item}")
            else:
                item.unlink()
                logger.info(f"已删除文件: {item}")
        except Exception as e:
            logger.error(f"删除 {item} 时出错: {e}")
            st.error(f"删除 {item} 时出错: {e}")


def edit_env(kb_path):
    """编辑 .env 文件"""
    env_path = kb_path / ".env"
    load_dotenv(dotenv_path=env_path)
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                env_content = f.read()
        except Exception as e:
            st.error(f"读取 .env 文件时出错: {e}")
            env_content = ""
    else:
        env_content = ""
    st.subheader(".env 文件编辑")
    new_env = st.text_area("编辑 .env 文件内容", env_content, height=200)
    if st.button("保存 .env 文件"):
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(new_env)
            st.success(".env 文件已保存！")
            rerun_method()  # 自动刷新页面
        except Exception as e:
            st.error(f"保存 .env 文件时出错: {e}")


def edit_settings(kb_path):
    """编辑 settings.yaml 文件"""
    settings_path = kb_path / "settings.yaml"
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_content = f.read()
        except Exception as e:
            st.error(f"读取 settings.yaml 文件时出错: {e}")
            settings_content = ""
    else:
        settings_content = ""
    st.subheader("settings.yaml 文件编辑")
    new_settings = st.text_area(
        "编辑 settings.yaml 文件内容", settings_content, height=600)
    if st.button("保存 settings.yaml 文件"):
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(new_settings)
            st.success("settings.yaml 文件已保存！")
            rerun_method()  # 自动刷新页面
        except Exception as e:
            st.error(f"保存 settings.yaml 文件时出错: {e}")


def manage_files(kb_path):
    """管理知识库中的 txt 文件"""
    input_path = kb_path / "input"
    st.subheader("管理知识库中的知识文件 (input 下的 txt 文件)")
    # 列出当前文件
    files = [f.name for f in input_path.glob("*.txt")]
    st.write("当前文件：")
    if files:
        for file in files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(file)
            with col2:
                if st.button(f"删除 {file}", key=f"del_{file}"):
                    try:
                        os.remove(input_path / file)
                        st.success(f"文件 '{file}' 已删除！")
                        print(f"文件 '{file}' 已删除！")
                        rerun_method()  # 自动刷新页面
                    except Exception as e:
                        st.error(f"删除文件 '{file}' 时出错: {e}")
    else:
        st.info("当前没有上传的 txt 文件。")
    st.write("---")
    # 上传文件
    uploaded_files = st.file_uploader(
        "上传新的 txt 文件", type=["txt"], accept_multiple_files=True)

    # 初始化 session state 标记
    if 'files_uploaded' not in st.session_state:
        st.session_state['files_uploaded'] = False

    if uploaded_files and not st.session_state['files_uploaded']:
        for uploaded_file in uploaded_files:
            save_path = input_path / uploaded_file.name
            try:
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                print(f"文件 '{uploaded_file.name}' 上传成功！")
            except Exception as e:
                st.error(f"上传文件 '{uploaded_file.name}' 时出错: {e}")
        st.success(f"共上传了 {len(uploaded_files)} 个文件。")
        # 设置标记以指示文件已上传
        st.session_state['files_uploaded'] = True  # 设置标记为已上传
        rerun_method()  # 自动刷新页面

    # 在页面重新加载后重置标记
    if st.session_state.get('files_uploaded', False):
        st.session_state['files_uploaded'] = False


def run_graphrag_command(args, cwd):
    """通过 subprocess 调用 graphrag 命令，并输出结果到控制台"""
    try:
        result = subprocess.run(
            ["python", "-m", "graphrag"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将stderr重定向到stdout
            text=True,
            check=True
        )
        print(f"Command Output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command Error: {e.output}")
        return f"Error: {e.output}"


def parse_graphrag_response(output, method):
    """解析 graphrag 命令的响应"""
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
    """索引指定的知识库"""
    kb_path = KB_DIR / name

    # 执行索引命令，并使用 spinner 显示加载动画
    with st.spinner("正在索引知识库..."):
        output = run_graphrag_command(
            ["index", "--root", str(kb_path)], cwd=ROOT_DIR)

    # 输出索引结果到控制台
    print(f"索引输出 for {name}: {output}")

    # 判断索引是否成功
    expected_message = "All workflows completed successfully."
    if expected_message in output:
        st.success("知识库索引成功！")
        logger.info(f"知识库 '{name}' 索引成功！")
        rerun_method()  # 自动刷新页面以显示最新内容
    else:
        st.error("索引失败，请检查 graphrag 是否正确安装或配置。")


# 主界面
st.title("GraphRAG Web UI")

menu = ["知识库管理", "知识库问答"]
choice = st.sidebar.selectbox("选择模块", menu)

if choice == "知识库管理":
    st.header("知识库管理")
    kb_list = list_knowledge_bases()

    col1, col2 = st.columns(2)
    with col1:
        new_kb = st.text_input("新建知识库名称")
        if st.button("添加知识库"):
            if new_kb:
                if new_kb in kb_list:
                    st.error("知识库名称已存在！")
                else:
                    success, message = create_knowledge_base(new_kb)
                    if success:
                        st.success(message)
                        rerun_method()  # 自动刷新页面
                    else:
                        st.error(message)
            else:
                st.error("请输入知识库名称！")
    with col2:
        if kb_list:
            del_kb = st.selectbox("选择要删除的知识库", [""] + kb_list, index=0)
            if st.button("删除知识库"):
                if del_kb and del_kb in kb_list:
                    success, message = delete_knowledge_base(del_kb)
                    if success:
                        st.success(message)
                        rerun_method()  # 自动刷新页面
                    else:
                        st.error(message)
                else:
                    st.error("请选择要删除的知识库！")
        else:
            st.info("当前没有任何知识库可以删除。")

    # 添加 Refresh button next to "现有知识库列表"
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("现有知识库列表")
    with col2:
        if st.button("刷新列表"):
            rerun_method()  # 手动触发页面重跑

    # 列出知识库
    if kb_list:
        for kb in kb_list:
            st.write(f"- {kb}")
    else:
        st.info("当前没有任何知识库。")

    st.write("---")

    # 选择知识库进行管理
    if kb_list:
        selected_kb = st.selectbox("选择一个知识库进行管理", kb_list, key="manage_select")
        if selected_kb:
            kb_path = KB_DIR / selected_kb
            st.write(f"当前管理的知识库： **{selected_kb}**")
            tab1, tab2, tab3, tab4 = st.tabs(
                ["修改 .env", "修改 settings.yaml", "管理知识文件", "索引知识库"])

            with tab1:
                edit_env(kb_path)

            with tab2:
                edit_settings(kb_path)

            with tab3:
                manage_files(kb_path)

            with tab4:
                st.subheader("索引知识库")
                st.write("点击下方按钮，使用 graphrag 对当前知识库进行索引。")

                # 添加复选框让用户选择是否清除缓存
                clear_cache_option = st.checkbox("清除缓存")

                if st.button("索引知识库", key=f"index_{selected_kb}"):
                    if clear_cache_option:
                        with st.spinner("正在清除缓存..."):
                            clear_cache(kb_path)
                        st.success("缓存已清除！")

                    index_knowledge_base(selected_kb)
    else:
        st.info("当前没有任何知识库可以管理。")

elif choice == "知识库问答":
    st.header("知识库问答")
    kb_list = list_knowledge_bases()
    if not kb_list:
        st.error("当前没有任何知识库，请先创建一个知识库。")
    else:
        selected_kb = st.selectbox("选择一个知识库进行提问", kb_list, key="qa_select")
        if selected_kb:
            kb_path = KB_DIR / selected_kb
            query = st.text_input("输入你的问题")
            method = st.selectbox("选择查询方法", ["local", "global", "drift"])
            if st.button("提交问题"):
                if query:
                    with st.spinner("正在处理你的问题，请稍候..."):
                        # 执行查询
                        args = ["query", "--root",
                                str(kb_path), "--method", method, "--query", query]
                        output = run_graphrag_command(args, cwd=ROOT_DIR)
                        # 解析响应
                        response = parse_graphrag_response(output, method)
                    print(f"查询输出 for {selected_kb}: {output}")
                    if response:
                        st.markdown(response)
                    else:
                        st.error("未找到有效的响应，可能知识库未初始化或出现其他错误。")
                else:
                    st.error("请输入你的问题！")
