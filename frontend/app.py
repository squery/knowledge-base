"""
前端Streamlit应用
"""
import streamlit as st
import requests
import json
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="本地知识库系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1em;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 全局变量
API_URL = "http://localhost:8000"
SIDEBAR_SECTIONS = ["📚 文件管理", "🔍 智能问答", "⚙️ 系统设置"]


def init_session_state():
    """初始化session状态"""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "📚 文件管理"


def check_api_health():
    """检查API服务是否运行"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def file_management_section():
    """文件管理部分"""
    st.header("📚 文件管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("上传文件")
        uploaded_files = st.file_uploader(
            "选择文件或文件夹",
            accept_multiple_files=True,
            help="支持文档(txt, pdf, docx, md, html)和代码文件(py, js, java等)"
        )
        
        if uploaded_files:
            st.info(f"选中 {len(uploaded_files)} 个文件")
            if st.button("开始上传", key="upload_btn"):
                st.success("文件上传功能待实现")
                st.progress(100)
    
    with col2:
        st.subheader("统计信息")
        st.metric("已上传文件", 0)
        st.metric("已索引文件", 0)
        st.metric("索引中文件", 0)
    
    # 文件列表
    st.subheader("已上传文件列表")
    if st.session_state.uploaded_files:
        # 创建表格显示文件
        file_data = []
        for f in st.session_state.uploaded_files:
            file_data.append({
                "文件名": f["name"],
                "大小(MB)": f"{f['size'] / (1024*1024):.2f}",
                "索引状态": f["status"],
                "操作": "删除"
            })
        st.dataframe(file_data, use_container_width=True)
    else:
        st.info("暂无上传文件")


def qa_section():
    """智能问答部分"""
    st.header("🔍 智能问答")
    
    # 对话历史显示
    st.subheader("对话记录")
    
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
    else:
        st.info("暂无对话记录")
    
    # 输入框
    st.subheader("提问")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "请输入您的问题",
            placeholder="输入问题...",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("发送", key="send_btn"):
            if user_input:
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                st.success("问答功能待实现")
                st.rerun()
    
    # 高级选项
    with st.expander("高级选项"):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider("温度(创意度)", 0.0, 1.0, 0.7)
        with col2:
            top_k = st.slider("检索文档数", 1, 10, 3)


def settings_section():
    """系统设置部分"""
    st.header("⚙️ 系统设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("模型设置")
        embedding_model = st.selectbox(
            "嵌入模型",
            ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "其他模型"]
        )
        llm_model = st.selectbox(
            "对话模型",
            ["ChatGLM-6B", "Qwen-7B", "其他模型"]
        )
        device = st.radio("运算设备", ["CPU", "CUDA"])
    
    with col2:
        st.subheader("文件设置")
        max_file_size = st.number_input("最大文件大小(MB)", value=100, min_value=10)
        chunk_size = st.number_input("分块大小(字符)", value=800, min_value=100)
        chunk_overlap = st.number_input("分块重叠(字符)", value=200, min_value=0)
    
    st.subheader("系统信息")
    if check_api_health():
        st.success("✅ API服务正常")
    else:
        st.error("❌ API服务未连接")
    
    if st.button("保存设置"):
        st.success("设置已保存")


def main():
    """主函数"""
    init_session_state()
    
    # 标题
    st.title("📚 本地知识库系统")
    st.markdown("支持文档和代码的智能检索与问答")
    
    # 检查API
    if not check_api_health():
        st.error("⚠️ 后端API服务未连接，请确保后端服务已启动 (http://localhost:8000)")
        st.info("运行命令启动后端: `python backend/main.py`")
    
    # 侧边栏导航
    with st.sidebar:
        st.title("导航")
        selected = st.radio("选择功能", SIDEBAR_SECTIONS, label_visibility="collapsed")
        
        st.divider()
        st.subheader("关于")
        st.info(
            "**本地知识库系统 v1.0.0**\n\n"
            "一个基于Python的本地知识库系统，"
            "支持文档和代码的智能检索和问答。"
        )
    
    # 根据选择显示对应部分
    if selected == "📚 文件管理":
        file_management_section()
    elif selected == "🔍 智能问答":
        qa_section()
    elif selected == "⚙️ 系统设置":
        settings_section()
    
    # 底部信息
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.caption("© 2024 本地知识库系统")
    with col3:
        st.caption("v1.0.0")


if __name__ == "__main__":
    main()
