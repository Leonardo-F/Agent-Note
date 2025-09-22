# 搜索翻译 mcp server

from mcp.server.fastmcp import FastMCP
from typing import Optional, Union, List, Dict
from pydantic import BaseModel
import os


# 创建MCP实例
mcp = FastMCP('search-translate-mcp')

# 根目录配置
# 将根目录设置为当前文件所在目录下的 .mcp-output 文件夹
DEFAULT_MCP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mcp-output')
_env_root = os.environ.get('MCP_ROOT')
if _env_root and os.path.isabs(_env_root):
    MCP_ROOT = _env_root
else:
    MCP_ROOT = DEFAULT_MCP_ROOT

def ensure_root_dir():
    """确保根目录存在"""
    try:
        os.makedirs(MCP_ROOT, exist_ok=True)
    except Exception as e:
        print(f"创建根目录时出错: {e}")
ensure_root_dir()
