import json
import requests
import hashlib
import random
from typing import Dict, List, Any


class ReactTools:
    """
    React Agent 工具类
    
    为 ReAct Agent 提供标准化的工具接口
    """
    
    def __init__(self) -> None:
        self.toolConfig = self._build_tool_config()
    
    def _build_tool_config(self) -> List[Dict[str, Any]]:
        """构建工具配置信息"""
        return [
            {
                'name_for_human': '谷歌搜索',
                'name_for_model': 'google_search',
                'description_for_model': '谷歌搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。',
                'parameters': [
                    {
                        'name': 'search_query',
                        'description': '搜索关键词或短语',
                        'required': True,
                        'schema': {'type': 'string'},
                    }
                ],
            },
            {
                'name_for_human': '百度翻译',
                'name_for_model': 'baidu_translate',
                'description_for_model': '百度翻译API，支持多种语言互译。',
                'parameters': [
                    {
                        'name': 'query',
                        'description': '需要翻译的文本',
                        'required': True,
                        'schema': {'type': 'string'},
                    },
                    {
                        'name': 'from_lang',
                        'description': '源语言代码，如zh,en等，其中 zh表示中文，en表示英语',
                        'required': True,
                        'schema': {'type': 'string'},
                    },
                    {
                        'name': 'to_lang',
                        'description': '目标语言代码，如zh,en,ja等，其中 zh表示中文，en表示英语',
                        'required': True,
                        'schema': {'type': 'string'},
                    },
                ],
            }
        ]
    
    def google_search(self, search_query: str) -> str:
        """执行谷歌搜索

        可在 https://serper.dev/dashboard 申请 api key

        Args:
            search_query: 搜索关键词
            
        Returns:
            格式化的搜索结果字符串
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
                formatted_results.append(f"{idx}. **{title}**\n   {snippet}\n   链接: {link}")
            
            return "\n\n".join(formatted_results) if formatted_results else "未找到相关结果"
            
        except Exception as e:
            return f"搜索时出现错误: {str(e)}"
    
    def baidu_translate(self, query: str, from_lang: str, to_lang: str) -> str:
        """执行百度翻译

        Args:
            query: 需要翻译的文本
            from_lang: 源语言代码
            to_lang: 目标语言代码
            app_id: 百度翻译API的APP ID
            secret_key: 百度翻译API的密钥
            
        Returns:
            翻译结果字符串
        """
        url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

        app_id = 'your baidu translate app id'
        secret_key = 'your baidu translate secret key'

        if not app_id or not secret_key:
            return "请提供百度翻译API的APP ID和密钥"
        
        if not from_lang or not to_lang:
            # 默认使用中文和英文
            from_lang = 'zh'
            to_lang = 'en'
            return "默认源语言为中文，目标语言为英文"
        
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
                return f"翻译失败，错误代码: {result['error_code']}"
            
            # 提取翻译结果
            if 'trans_result' in result and result['trans_result']:
                translated_text = '\n'.join([item['dst'] for item in result['trans_result']])
                return translated_text
            else:
                return "未找到翻译结果"
                
        except Exception as e:
            return f"翻译时出现错误: {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具名称列表"""
        return [tool['name_for_model'] for tool in self.toolConfig]
    
    def get_tool_description(self, tool_name: str) -> str:
        """获取工具描述"""
        for tool in self.toolConfig:
            if tool['name_for_model'] == tool_name:
                return tool['description_for_model']
        return "未知工具"

if __name__ == "__main__":
    tools = ReactTools()
    print("谷歌搜索结果：")
    result = tools.google_search("什么是量子计算？")
    print(result)

    # 中文翻译成英文
    print("中文翻译成英文：")
    result_translate = tools.baidu_translate("s", "zh", "en")
    print(result_translate)



