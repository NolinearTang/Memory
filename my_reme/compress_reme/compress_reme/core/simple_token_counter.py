"""简单的 Token Counter 实现

规则：
- 中文字符：1个字 = 1个token
- 英文字符：4个字符 = 1个token
"""

import re


class SimpleTokenCounter:
    """简单的 token 计数器，不依赖外部模型"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def get_num_tokens(self, text: str) -> int:
        """计算文本的 token 数
        
        Args:
            text: 要计算的文本
            
        Returns:
            token 数量
        """
        if not text:
            return 0
        
        # 统计中文字符（包括中文标点）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))
        
        # 移除中文字符后计算英文
        text_without_chinese = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', text)
        
        # 英文和数字等按4个字符算1个token
        english_tokens = len(text_without_chinese) // 4
        
        # 总 tokens = 中文字符数 + 英文tokens
        total_tokens = chinese_chars + english_tokens
        
        return total_tokens
    
    def count_messages(self, messages: list) -> int:
        """计算消息列表的总 token 数
        
        Args:
            messages: 消息列表，每个消息是 Msg 对象
            
        Returns:
            总 token 数
        """
        total = 0
        for msg in messages:
            # 获取消息内容
            content = getattr(msg, 'content', '') or ''
            total += self.get_num_tokens(content)
        return total
