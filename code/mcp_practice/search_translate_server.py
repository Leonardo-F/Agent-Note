# 搜索翻译 mcp server

import json
import requests
import hashlib
import random
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

def get_output_path(name: str) -> str:
    """根据文件名称返回文件存储路径"""
    return os.path.join(MCP_ROOT, f"{name}.md")

class SearchResult(BaseModel):
    success: bool
    message: str
    output: Optional[Union[str, List[Dict]]] = None

class TranslateResult(BaseModel):
    success: bool
    message: str
    output: Optional[str] = None

class OutputResult(BaseModel):
    success: bool
    message: str
    output: Optional[str] = None

@mcp.prompt()
def search_translate_prompt():
    """指导 AI 使用搜索和翻译工具"""
    return """
 你是一个擅长搜索和翻译的助手。你可以帮助用户搜索相关信息，然后将搜索结果翻译成双语，并输出到markdown文件中。

 可用的操作包括：
 1. google_search: 搜索相关信息
 2. baidu_translate: 翻译文本
 3. format_output: 将搜索结果和翻译结果格式化输出到markdown文件

 请根据用户的需求选择合适的工具进行操作。
 """

@mcp.tool()
def google_search(search_query: str) -> SearchResult:
    """
    执行谷歌搜索
    `search_query`: 搜索关键词或短语
    """
    url = "https://google.serper.dev/search"

    payload = json.dumps({"q": search_query})
    headers = {
        'X-API-KEY': 'your serper api key',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload).json()
        organic_results = response.get('organic', [])
        
        # 格式化搜索结果
        formatted_results = []
        for idx, result in enumerate(organic_results[:5], 1):
            title = result.get('title', '无标题')
            snippet = result.get('snippet', '无描述')
            link = result.get('link', '')
            formatted_results.append({
                "title": title,
                "snippet": snippet,
                "link": link
            })
        
        return SearchResult(
            success=True,
            message=f"搜索完成，找到{len(formatted_results)}个结果",
            output=formatted_results
        )
        
    except Exception as e:
        return SearchResult(
            success=False,
            message=f"搜索时出现错误: {str(e)}"
        )

@mcp.tool()
def baidu_translate(query: str, from_lang: str, to_lang: str) -> TranslateResult:
    """
    执行百度翻译
    `query`: 需要翻译的文本
    `from_lang`: 源语言代码
    `to_lang`: 目标语言代码
    """
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    app_id = 'your baidu translate app id'
    secret_key = 'your baidu translate secret key'

    if not app_id or not secret_key:
        return TranslateResult(
            success=False,
            message="请提供百度翻译API的APP ID和密钥"
        )
    
    # 生成随机数
    salt = random.randint(32768, 65536)
    # 生成签名
    sign_str = app_id + query + str(salt) + secret_key
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    # 构建请求参数
    params = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': app_id,
        'salt': salt,
        'sign': sign
    }
    
    try:
        response = requests.get(url, params=params)
        result = response.json()
        
        # 检查是否有错误
        if 'error_code' in result:
            return TranslateResult(
                success=False,
                message=f"翻译失败，错误代码: {result['error_code']}"
            )
        
        # 提取翻译结果
        if 'trans_result' in result and result['trans_result']:
            translated_text = '\n'.join([item['dst'] for item in result['trans_result']])
            return TranslateResult(
                success=True,
                message="翻译成功",
                output=translated_text
            )
        else:
            return TranslateResult(
                success=False,
                message="未找到翻译结果"
            )
            
    except Exception as e:
        return TranslateResult(
            success=False,
            message=f"翻译时出现错误: {str(e)}"
        )

@mcp.tool()
def format_output(search_results: List[Dict], translated_results: List[str], filename: str) -> OutputResult:
    """
    将搜索结果和翻译结果格式化输出到markdown文件
    `search_results`: 搜索结果列表
    `translated_results`: 翻译结果列表
    `filename`: 输出文件名（不需要包含.md扩展名）
    """
    try:
        output_path = get_output_path(filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入标题
            f.write("# 搜索与翻译结果\n\n")
            
            # 写入搜索结果和翻译结果
            for i, (search_item, translated_text) in enumerate(zip(search_results, translated_results), 1):
                f.write(f"## {i}. {search_item['title']}\n\n")
                f.write(f"**原文:**\n\n{search_item['snippet']}\n\n")
                f.write(f"**译文:**\n\n{translated_text}\n\n")
                f.write(f"[链接]({search_item['link']})\n\n")
                f.write("---\n\n")
        
        return OutputResult(
            success=True,
            message=f"输出文件创建成功",
            output=output_path
        )
        
    except Exception as e:
        return OutputResult(
            success=False,
            message=f"创建输出文件时出现错误: {str(e)}"
        )

    