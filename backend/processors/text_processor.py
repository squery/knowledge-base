"""
文本处理模块
支持多种文件格式的解析和文本分块
"""
import os
from typing import List, Tuple, Optional
from pathlib import Path
import re
import sys

# 添加后端目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from logger_config import get_logger
from config import settings

logger = get_logger(__name__)


class TextChunk:
    """文本分块对象"""
    def __init__(self, content: str, metadata: dict = None):
        self.content = content
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"<TextChunk(len={len(self.content)}, metadata={self.metadata})>"


class TextProcessor:
    """文本处理器"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        初始化文本处理器
        
        Args:
            chunk_size: 分块大小(字符数)
            chunk_overlap: 分块重叠(字符数)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        logger.info(f"文本处理器初始化: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def process_file(self, file_path: str, file_type: str = None) -> List[TextChunk]:
        """
        处理文件并返回文本分块列表
        
        Args:
            file_path: 文件路径
            file_type: 文件类型(document/code)
            
        Returns:
            TextChunk列表
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 根据文件类型选择解析方法
        if ext == '.txt':
            text = self._read_text_file(file_path)
        elif ext == '.md':
            text = self._read_markdown_file(file_path)
        elif ext == '.pdf':
            text = self._read_pdf_file(file_path)
        elif ext == '.docx':
            text = self._read_docx_file(file_path)
        elif ext == '.html' or ext == '.htm':
            text = self._read_html_file(file_path)
        elif ext in ['.py', '.js', '.java', '.cpp', '.go', '.rs', '.ts', '.jsx', '.tsx', '.cs']:
            text = self._read_code_file(file_path)
        elif ext == '.pcd':
            text = self._read_pcd_file(file_path)
        else:
            logger.warning(f"未知的文件类型: {ext}, 按纯文本处理")
            text = self._read_text_file(file_path)
        
        # 分块处理
        chunks = self._chunk_text(text, file_path)
        logger.info(f"文件处理完成: {file_path} -> {len(chunks)} 个分块")
        
        return chunks
    
    def _read_text_file(self, file_path: str) -> str:
        """读取纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                return f.read()
    
    def _read_markdown_file(self, file_path: str) -> str:
        """读取Markdown文件"""
        return self._read_text_file(file_path)
    
    def _read_pdf_file(self, file_path: str) -> str:
        """读取PDF文件"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page_num, page in enumerate(doc):
                text += f"\n--- 第 {page_num + 1} 页 ---\n"
                text += page.get_text()
            return text
        except ImportError:
            logger.error("PyMuPDF 未安装, 请执行: pip install pymupdf")
            raise
    
    def _read_docx_file(self, file_path: str) -> str:
        """读取DOCX文件"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except ImportError:
            logger.error("python-docx 未安装, 请执行: pip install python-docx")
            raise
    
    def _read_html_file(self, file_path: str) -> str:
        """读取HTML文件"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                # 移除script和style
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text(separator='\n')
        except ImportError:
            logger.error("beautifulsoup4 未安装, 请执行: pip install beautifulsoup4")
            # 降级方案: 直接读取
            return self._read_text_file(file_path)
    
    def _read_pcd_file(self, file_path: str) -> str:
        """
        读取PCD点云文件
        解析文件头部元数据，并在数据为ASCII格式时采样部分点数据
        """
        _PCD_FORMAT_UNKNOWN = "unknown"
        _MAX_PCD_SAMPLE_POINTS = 20

        file_name = os.path.basename(file_path)
        header_lines = []
        data_format = _PCD_FORMAT_UNKNOWN
        fields = []
        num_points = 0
        sample_points = []

        try:
            with open(file_path, 'rb') as f:
                for raw_line in f:
                    try:
                        line = raw_line.decode('utf-8', errors='ignore').rstrip()
                    except UnicodeDecodeError as e:
                        logger.warning(f"PCD文件头部解码失败: {file_path}, 错误: {e}")
                        break

                    header_lines.append(line)

                    lower = line.lower()
                    if lower.startswith('fields'):
                        fields = line.split()[1:]
                    elif lower.startswith('points'):
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                num_points = int(parts[1])
                            except ValueError:
                                pass
                    elif lower.startswith('data'):
                        parts = line.split()
                        if len(parts) >= 2:
                            data_format = parts[1].lower()
                        break

                # 如果是ASCII格式，采样最多 _MAX_PCD_SAMPLE_POINTS 行点数据
                if data_format == 'ascii':
                    for raw_line in f:
                        try:
                            line = raw_line.decode('utf-8', errors='ignore').rstrip()
                        except UnicodeDecodeError as e:
                            logger.warning(f"PCD点数据解码失败: {file_path}, 错误: {e}")
                            break
                        if line:
                            sample_points.append(line)
                        if len(sample_points) >= _MAX_PCD_SAMPLE_POINTS:
                            break

        except Exception as e:
            logger.warning(f"读取PCD文件失败: {file_path}, 错误: {e}")
            return f"文件名: {file_name}\n文件类型: PCD点云文件\n(文件读取失败)\n"

        header_text = '\n'.join(header_lines)
        result = f"""文件名: {file_name}
文件类型: PCD 3D点云文件
点云数量: {num_points}
字段列表: {' '.join(fields) if fields else '未知'}
数据格式: {data_format}

--- PCD文件头部 ---
{header_text}
"""
        if sample_points:
            result += f"\n--- 点数据采样(前{len(sample_points)}行, 共{num_points}点) ---\n"
            result += '\n'.join(sample_points)

        return result

    def _read_code_file(self, file_path: str) -> str:
        """读取代码文件(保留结构信息和函数/类上下文)"""
        text = self._read_text_file(file_path)
        
        # 添加文件信息头
        file_name = os.path.basename(file_path)
        _, ext = os.path.splitext(file_path)
        
        # 尝试解析代码结构（函数、类、注释）
        structured_text = self._parse_code_structure(text, ext)
        
        header = f"""
文件名: {file_name}
文件类型: {ext}
代码内容:
--- 开始 ---
"""
        return header + structured_text + "\n--- 结束 ---"
    
    def _parse_code_structure(self, code: str, ext: str) -> str:
        """
        解析代码结构，提取函数、类、注释等关键信息
        
        Args:
            code: 源代码文本
            ext: 文件扩展名
            
        Returns:
            带结构标记的代码文本
        """
        # 简化版：为主要语言添加结构标记
        lines = code.split('\n')
        annotated_lines = []
        
        # Python代码结构识别
        if ext == '.py':
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                # 识别类定义
                if stripped.startswith('class '):
                    class_name = stripped.split('(')[0].replace('class ', '').strip(':')
                    annotated_lines.append(f"[类定义: {class_name}]")
                # 识别函数定义
                elif stripped.startswith('def '):
                    func_name = stripped.split('(')[0].replace('def ', '')
                    annotated_lines.append(f"[函数: {func_name}]")
                annotated_lines.append(line)
        
        # JavaScript/TypeScript代码结构识别
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            for line in lines:
                stripped = line.lstrip()
                # 识别类定义
                if stripped.startswith('class '):
                    class_name = stripped.split('{')[0].replace('class ', '').strip()
                    annotated_lines.append(f"[类定义: {class_name}]")
                # 识别函数定义
                elif re.match(r'(function\s+\w+|const\s+\w+\s*=.*=>|async\s+function)', stripped):
                    func_match = re.search(r'(function\s+(\w+)|const\s+(\w+))', stripped)
                    if func_match:
                        func_name = func_match.group(2) or func_match.group(3)
                        annotated_lines.append(f"[函数: {func_name}]")
                annotated_lines.append(line)
        
        # Java代码结构识别
        elif ext == '.java':
            for line in lines:
                stripped = line.lstrip()
                # 识别类定义
                if re.match(r'(public|private|protected)?\s*(class|interface|enum)\s+\w+', stripped):
                    class_match = re.search(r'(class|interface|enum)\s+(\w+)', stripped)
                    if class_match:
                        annotated_lines.append(f"[{class_match.group(1)}: {class_match.group(2)}]")
                # 识别方法定义
                elif re.match(r'(public|private|protected)?\s*\w+\s+\w+\s*\(', stripped):
                    method_match = re.search(r'\s(\w+)\s*\(', stripped)
                    if method_match:
                        annotated_lines.append(f"[方法: {method_match.group(1)}]")
                annotated_lines.append(line)
        
        # 其他语言直接返回原始代码
        else:
            return code
        
        return '\n'.join(annotated_lines)
    
    def _chunk_text(self, text: str, file_path: str = None) -> List[TextChunk]:
        """
        将文本分块
        
        Args:
            text: 原始文本
            file_path: 文件路径(用于元数据)
            
        Returns:
            TextChunk列表
        """
        # 清理文本
        text = self._clean_text(text)
        
        if not text:
            logger.warning(f"文本为空: {file_path}")
            return []
        
        chunks = []
        
        # 首先尝试按段落分割(保留上下文)
        # 按双换行符分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果添加此段落会超过chunk_size
            if len(current_chunk) + len(para) + 1 > self.chunk_size:
                # 保存当前分块
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk.strip(), file_path, len(chunks)))
                
                # 如果单个段落太长,需要进一步分割
                if len(para) > self.chunk_size:
                    sub_chunks = self._chunk_long_text(para, file_path, len(chunks))
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para
            else:
                # 添加到当前分块
                if current_chunk:
                    current_chunk += "\n" + para
                else:
                    current_chunk = para
        
        # 保存最后的分块
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk.strip(), file_path, len(chunks)))
        
        return chunks
    
    def _chunk_long_text(self, text: str, file_path: str, start_idx: int = 0) -> List[TextChunk]:
        """
        分割长文本(简单按固定大小分割)
        
        Args:
            text: 长文本
            file_path: 文件路径
            start_idx: 起始索引
            
        Returns:
            TextChunk列表
        """
        chunks = []
        text_len = len(text)
        
        i = 0
        while i < text_len:
            # 计算分块结束位置
            end = min(i + self.chunk_size, text_len)
            
            # 尝试在词边界处截断(向前查找换行符或空格)
            if end < text_len:
                # 向前查找最后的换行符或空格
                last_break = max(
                    text.rfind('\n', i, end),
                    text.rfind(' ', i, end)
                )
                if last_break > i:
                    end = last_break + 1
            
            chunk_text = text[i:end].strip()
            if chunk_text:
                chunks.append(self._create_chunk(chunk_text, file_path, start_idx + len(chunks)))
            
            # 移动到下一个分块
            i = end - self.chunk_overlap if end < text_len else text_len
        
        return chunks
    
    def _create_chunk(self, content: str, file_path: str = None, chunk_idx: int = 0) -> TextChunk:
        """
        创建TextChunk对象
        
        Args:
            content: 分块内容
            file_path: 源文件路径
            chunk_idx: 分块索引
            
        Returns:
            TextChunk对象
        """
        metadata = {
            "source": file_path or "unknown",
            "chunk_index": chunk_idx,
            "content_length": len(content)
        }
        
        return TextChunk(content, metadata)
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # 多个空行合并为两个
        text = re.sub(r'[ \t]+', ' ', text)  # 多个空格合并为一个
        text = text.strip()
        
        return text


# 全局处理器实例
processor = TextProcessor()
