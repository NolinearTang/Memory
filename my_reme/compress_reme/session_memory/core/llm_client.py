import asyncio
import re
import aiohttp
import json


class LlmClient:
    def __init__(self, config):
        # 保存 model_hub 配置
        self.model_hub = config.get("model_hub", {})

    @staticmethod
    def remove_think_tags(content):
        patt = r'<think>.*?</think>'
        cleaned_content = re.sub(patt, '', content, flags=re.DOTALL)
        return cleaned_content.strip()

    @staticmethod
    def get_label_tags(content):
        match = re.search(r'<label>(.*?)</label>', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return None

    @staticmethod
    def get_score_tags(content):
        match = re.search(r'<score>(.*?)</score>', content, re.DOTALL)
        if match:
            return float(match.group(1).strip())
        else:
            return 0.0

    def _get_model_config(self, model_name):
        """根据 model_name 获取模型配置"""
        if model_name not in self.model_hub:
            raise ValueError(f"Model '{model_name}' not found in model_hub")

        model_config = self.model_hub[model_name].copy()
        return model_config

    def _build_headers(self, api_key):
        """构建请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def _build_body(self, model_config, prompt, content, max_tokens=None, **kwargs):
        """构建请求体"""
        body = {
            "model": model_config.get('model_name'),
            "stream": False,
            "n": 1,
            "top_p": 0.9,
            "temperature": model_config.get("temperature", 0.0),
            "max_tokens": max_tokens if max_tokens else model_config.get("max_tokens", 1024),
            "repetition_penalty": model_config.get("repetition_penalty", 1.1),
            "seed":  model_config.get("seed", 42),
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        # 更新额外参数
        if kwargs:
            body.update(kwargs)

        return body

    async def do_llm(self, model_name, prompt, content, max_tokens=None, **kwargs):
        """
        非流式调用

        Args:
            model_name: 模型名称，从 model_hub 中查找配置
            prompt: 系统提示词
            content: 用户输入内容
            max_tokens: 最大token数
            **kwargs: 额外参数，如 api_key 等
        """
        # 获取模型配置
        model_config = self._get_model_config(model_name)

        # 优先使用传入的 api_key
        api_key = kwargs.pop('api_key', model_config.get('api_key'))

        # 构建请求
        headers = self._build_headers(api_key)
        body = self._build_body(model_config, prompt, content, max_tokens, **kwargs)
        url = model_config.get('base_url') + "/chat/completions"

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(
                        url,
                        json=body,
                        headers=headers,
                ) as response:
                    result = await response.json()
                    content = result["choices"][0].get("message").get("content")
                    return content
        except Exception as e:
            print(f"非流式请求发生错误: {e}")
            return ''

    async def stream_llm(self, model_name, prompt, content, max_tokens=None, **kwargs):
        """
        流式调用

        Args:
            model_name: 模型名称，从 model_hub 中查找配置
            prompt: 系统提示词
            content: 用户输入内容
            max_tokens: 最大token数
            **kwargs: 额外参数，如 api_key 等
        """
        # 获取模型配置
        model_config = self._get_model_config(model_name)

        # 优先使用传入的 api_key
        api_key = kwargs.pop('api_key', model_config['api_key'])

        # 构建请求
        headers = self._build_headers(api_key)
        body = self._build_body(model_config, prompt, content, max_tokens, **kwargs)
        body["stream"] = True  # 启用流式响应


        url = model_config.get('base_url') + "/chat/completions"

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(
                        url,
                        json=body,
                        headers=headers,
                        timeout=None,
                        ssl=False
                ) as response:
                    buffer = b''
                    async for data in response.content.iter_any():
                        if data:
                            buffer += data
                            while b'\n' in buffer:
                                line, buffer = buffer.split(b'\n', 1)
                                line = line.decode('utf-8').strip()
                                if not line:
                                    continue
                                if line.startswith('data: '):
                                    line = line[6:].strip()
                                    if line == '[DONE]':
                                        return
                                    try:
                                        chunk = json.loads(line)
                                        if chunk.get("choices") and len(chunk["choices"]) > 0:
                                            delta = chunk["choices"][0].get("delta", {})
                                            content = delta.get("content", "")
                                            if content:
                                                yield content
                                        elif "error" in chunk:
                                            print(f"API错误: {chunk['error']}")
                                            return
                                    except json.JSONDecodeError:
                                        continue
        except Exception as e:
            print(f"流式请求发生错误: {e}")
            yield ''


async def main():
    print("非流式调用")
    from kllm.src.config.config import kllm_config
    from kllm.src.intent.prompt_template.knowledge_intent_prompt_template import query_rewrite_new

    # 初始化 LlmClient，传入包含 model_hub 的配置
    llm_client = LlmClient(kllm_config)

    """
    config样例：
    {
        "model_hub": {
            "Qwen2.5-14B-Instruct": {
                "model_name": "Qwen2.5-14B-Instruct",
                "base_url": "http://10.68.250.54:10899/v1",
                "api_key": "gpustack_5a077616b6d6cdee_dfc1000d261c175066c3d784c0bf2185",
                "temperature": 0.0,
                "max_tokens": 5000,
                "repetition_penalty": 1.1
            },
            "other_model": {
                "model_name": "other_model",
                "base_url": "...",
                "api_key": "...",
                ...
            }
        }
    }
    """

    # 调用时传入 model_name
    model_name = "Qwen3-30B"  # 例如: "Qwen2.5-14B-Instruct"

    # param 可以不传   这个是适配动态api_key的
    param = {"temperature": 0.5}
    res = await llm_client.do_llm(model_name, "按要求写一个100字的故事", "无聊的", **param)
    print(res)

    print("======================分割线===================\n")
    print("流式调用")

    # 测试流式调用，可以传入不同的 api_key
    print("\n流式结果:")
    async for chunk in llm_client.stream_llm(model_name, "按要求写一个100字的故事", "搞笑的"):
        print(chunk, end='', flush=True)
    print()  # 换行

    # 测试使用自定义 api_key
    print("\n使用自定义 api_key 的流式结果:")
    custom_api_key = "your_custom_api_key_here"
    async for chunk in llm_client.stream_llm(model_name, "按要求写一个100字的故事", "惊悚的", api_key=custom_api_key):
        print(chunk, end='', flush=True)
    print()  # 换行


if __name__ == '__main__':
    asyncio.run(main())