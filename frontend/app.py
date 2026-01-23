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
    /* Sidebar navigation radio styles to avoid white-on-white check effect */
    .sidebar-nav div[role="radiogroup"] > label {
        border-radius: 10px;
        padding: 6px 10px;
        margin-bottom: 6px;
        transition: all 0.2s ease;
    }
    .sidebar-nav div[role="radiogroup"] > label:hover {
        background: #f4f6fb;
    }
    .sidebar-nav div[role="radiogroup"] > label input:checked + div {
        background: linear-gradient(120deg, #2563eb, #10b981);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.25);
        color: #ffffff;
    }
    .sidebar-nav div[role="radiogroup"] > label input:checked + div p {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 全局变量
API_URL = "http://localhost:8000"
SIDEBAR_SECTIONS = ["📚 文件管理", "🔍 智能问答", "📊 索引管理", "⚙️ 系统设置"]


def init_session_state():
    """初始化session状态"""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "🔍 智能问答"


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
    
    # 获取统计信息
    stats = get_statistics()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("上传文件")
        uploaded_files = st.file_uploader(
            "选择文件",
            accept_multiple_files=True,
            help="支持文档(txt, pdf, docx, md, html)和代码文件(py, js, java等)",
            key="file_uploader"
        )
        
        if uploaded_files:
            st.info(f"选中 {len(uploaded_files)} 个文件")
            if st.button("开始上传", key="upload_btn"):
                upload_files(uploaded_files)
    
    with col2:
        st.subheader("统计信息")
        if stats:
            st.metric("总文件数", stats.get("total_files", 0))
            st.metric("已索引", stats.get("indexed_count", 0))
            st.metric("待索引", stats.get("pending_count", 0))
        else:
            st.metric("总文件数", 0)
            st.metric("已索引", 0)
            st.metric("待索引", 0)
    
    # 文件列表
    st.subheader("已上传文件列表")
    
    # 过滤选项
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_type = st.selectbox(
            "文件类型",
            ["全部", "文档(document)", "代码(code)"],
            key="filter_type"
        )
    with col2:
        filter_status = st.selectbox(
            "索引状态",
            ["全部", "待索引(pending)", "索引中(indexing)", "已索引(indexed)", "失败(failed)"],
            key="filter_status"
        )
    with col3:
        if st.button("🔄 刷新", key="refresh_btn"):
            st.rerun()
    
    # 获取文件列表
    file_type_param = None if filter_type == "全部" else filter_type.split("(")[1].rstrip(")")
    status_param = None if filter_status == "全部" else filter_status.split("(")[1].rstrip(")")
    
    files = get_file_list(file_type_param, status_param)
    
    if files:
        # 选择要删除的文件
        selected_files = []
        
        for idx, file in enumerate(files):
            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
            
            with col1:
                st.text(file.get("original_filename", "未知"))
            with col2:
                file_size_mb = file.get("file_size", 0) / (1024 * 1024)
                st.text(f"{file_size_mb:.2f} MB")
            with col3:
                file_type = file.get("file_type", "未知")
                st.text(file_type)
            with col4:
                status = file.get("index_status", "未知")
                status_emoji = {
                    "pending": "⏳",
                    "indexing": "🔄",
                    "indexed": "✅",
                    "failed": "❌"
                }
                st.text(f"{status_emoji.get(status, '')} {status}")
            with col5:
                if st.checkbox("选择", key=f"select_{file['id']}", label_visibility="collapsed"):
                    selected_files.append(file['id'])
            with col6:
                if st.button("🗑️", key=f"del_{file['id']}", help="删除文件"):
                    delete_file(file['id'])
        
        # 批量删除
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col2:
            if selected_files and st.button("批量删除选中", key="batch_delete_btn"):
                batch_delete_files(selected_files)
    else:
        st.info("暂无上传文件")


def get_statistics():
    """获取统计信息"""
    try:
        response = requests.get(f"{API_URL}/api/files/statistics", timeout=5)
        if response.status_code == 200:
            return response.json().get("data", {})
    except Exception as e:
        st.error(f"获取统计信息失败: {str(e)}")
    return None


def get_file_list(file_type=None, index_status=None):
    """获取文件列表"""
    try:
        params = {}
        if file_type:
            params["file_type"] = file_type
        if index_status:
            params["index_status"] = index_status
        
        response = requests.get(f"{API_URL}/api/files/list", params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        st.error(f"获取文件列表失败: {str(e)}")
    return []


def upload_files(files):
    """上传文件"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(files)
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for idx, file in enumerate(files):
        try:
            status_text.text(f"正在上传: {file.name} ({idx + 1}/{total})")
            
            # 读取文件内容
            file_content = file.read()
            
            # 上传到后端
            files_data = {"file": (file.name, file_content, file.type)}
            response = requests.post(
                f"{API_URL}/api/files/upload",
                files=files_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            st.error(f"上传 {file.name} 失败: {str(e)}")
            failed_count += 1
        
        progress_bar.progress((idx + 1) / total)
    
    progress_bar.empty()
    status_text.empty()
    
    if success_count > 0:
        st.success(f"✅ 成功上传 {success_count} 个文件")
    if failed_count > 0:
        st.error(f"❌ 失败 {failed_count} 个文件")
    if skipped_count > 0:
        st.warning(f"⏭️ 跳过 {skipped_count} 个文件(已存在)")
    
    st.rerun()


def delete_file(file_id):
    """删除单个文件"""
    try:
        response = requests.delete(f"{API_URL}/api/files/{file_id}", timeout=5)
        if response.status_code == 200:
            st.success("文件删除成功")
            st.rerun()
        else:
            st.error("文件删除失败")
    except Exception as e:
        st.error(f"删除文件失败: {str(e)}")


def batch_delete_files(file_ids):
    """批量删除文件"""
    try:
        response = requests.post(
            f"{API_URL}/api/files/delete/batch",
            json=file_ids,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            st.success(result.get("message", "批量删除完成"))
            st.rerun()
        else:
            st.error("批量删除失败")
    except Exception as e:
        st.error(f"批量删除失败: {str(e)}")


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


def index_management_section():
    """索引管理部分"""
    st.header("📊 索引管理")
    
    # 获取索引状态
    try:
        response = requests.get(f"{API_URL}/api/index/status", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            
            # 统计信息卡片
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "总文件数",
                    stats.get("total_files", 0)
                )
            with col2:
                st.metric(
                    "已索引",
                    stats.get("indexed_files", 0)
                )
            with col3:
                st.metric(
                    "待索引",
                    stats.get("pending_files", 0)
                )
            with col4:
                st.metric(
                    "索引中",
                    stats.get("indexing_files", 0)
                )
            with col5:
                st.metric(
                    "失败",
                    stats.get("failed_files", 0)
                )
            
            # 索引进度
            st.subheader("索引进度")
            total_chunks = stats.get("total_chunks", 0)
            vector_count = stats.get("vector_count", 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("总分块数", total_chunks)
            with col2:
                st.metric("向量库数", vector_count)
            
            # 索引比例
            st.progress(
                float(stats.get("index_ratio", "0%").rstrip("%")) / 100.0,
                text=f"索引完成率: {stats.get('index_ratio', '0%')}"
            )
            
        else:
            st.error(f"获取索引状态失败: {response.status_code}")
            
    except Exception as e:
        st.error(f"获取索引状态出错: {str(e)}")
    
    # 索引操作
    st.subheader("索引操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 批量索引", use_container_width=True):
            with st.spinner("正在重建索引..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/index/rebuild",
                        timeout=300
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success(result.get("message", "重建成功"))
                        st.json(result.get("stats", {}))
                    else:
                        st.error(f"重建失败: {response.status_code}")
                except Exception as e:
                    st.error(f"重建失败: {str(e)}")
    
    with col2:
        if st.button("🔍 刷新状态", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("❌ 清空索引", use_container_width=True):
            st.warning("此操作将清空所有索引，无法恢复！")
            if st.button("确认清空", key="confirm_clear"):
                st.info("清空功能待实现")
    
    # 文件索引详情
    st.subheader("文件索引详情")
    
    try:
        response = requests.get(f"{API_URL}/api/files/list", timeout=5)
        if response.status_code == 200:
            files = response.json().get("data", {}).get("items", [])
            
            if files:
                # 创建表格数据
                table_data = []
                for file in files:
                    status = file.get("index_status", "未知")
                    status_emoji = {
                        "pending": "⏳",
                        "indexing": "⏳",
                        "indexed": "✅",
                        "failed": "❌"
                    }.get(status, "❓")
                    
                    table_data.append({
                        "文件名": file.get("original_filename", "未知"),
                        "状态": f"{status_emoji} {status}",
                        "分块数": file.get("chunk_count", 0),
                        "文件大小": f"{file.get('file_size', 0) / (1024*1024):.2f} MB",
                        "上传时间": file.get("upload_time", "未知")[:10] if file.get("upload_time") else "未知"
                    })
                
                # 显示表格
                st.dataframe(table_data, use_container_width=True)
                
                # 单个文件操作
                st.subheader("单个文件操作")
                selected_filename = st.selectbox(
                    "选择要操作的文件",
                    [f["original_filename"] for f in files],
                    key="file_select"
                )
                
                selected_file = next(
                    (f for f in files if f["original_filename"] == selected_filename),
                    None
                )
                
                if selected_file:
                    file_id = selected_file.get("id")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔄 重新索引", use_container_width=True):
                            with st.spinner(f"正在索引 {selected_filename}..."):
                                try:
                                    response = requests.post(
                                        f"{API_URL}/api/index/files/{file_id}",
                                        timeout=60
                                    )
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.success(result.get("message", "索引成功"))
                                    else:
                                        st.error(f"索引失败: {response.status_code}")
                                except Exception as e:
                                    st.error(f"索引失败: {str(e)}")
                    
                    with col2:
                        if st.button("🗑️ 删除索引", use_container_width=True):
                            try:
                                response = requests.delete(
                                    f"{API_URL}/api/index/files/{file_id}",
                                    timeout=10
                                )
                                if response.status_code == 200:
                                    st.success("索引已删除")
                                    st.rerun()
                                else:
                                    st.error(f"删除失败: {response.status_code}")
                            except Exception as e:
                                st.error(f"删除失败: {str(e)}")
            else:
                st.info("暂无文件")
                
        else:
            st.error(f"获取文件列表失败: {response.status_code}")
            
    except Exception as e:
        st.error(f"获取文件列表出错: {str(e)}")
    
    # 语义搜索
    st.subheader("语义搜索测试")
    search_query = st.text_input("输入搜索文本")
    top_k = st.slider("返回结果数", 1, 10, 3)
    
    if search_query and st.button("搜索", use_container_width=True):
        with st.spinner("搜索中..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/index/search",
                    params={"query": search_query, "top_k": top_k},
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success(f"找到 {result.get('total_results', 0)} 条相关结果")
                    
                    for i, item in enumerate(result.get("results", []), 1):
                        with st.expander(f"结果 {i} - 相似度: {item.get('similarity', 0):.2%}"):
                            st.write(f"**内容:** {item.get('content', '')[:200]}...")
                            st.caption(f"📁 {item.get('file_path', '未知')}")
                            if item.get('chunk_index') is not None:
                                st.caption(f"📍 分块 #{item.get('chunk_index', 0)}")
                else:
                    st.error(f"搜索失败: {response.status_code}")
            except Exception as e:
                st.error(f"搜索出错: {str(e)}")


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
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        selected = st.radio(
            "选择功能",
            SIDEBAR_SECTIONS,
            index=SIDEBAR_SECTIONS.index(st.session_state.selected_tab),
            label_visibility="collapsed",
        )
        st.session_state.selected_tab = selected
        st.markdown('</div>', unsafe_allow_html=True)
        
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
    elif selected == "📊 索引管理":
        index_management_section()
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
