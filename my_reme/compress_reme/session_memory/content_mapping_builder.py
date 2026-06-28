#!/usr/bin/env python3
"""
内容映射构建器（简化版）

功能：
1. 构建 content_list：所有content的列表
2. 构建 sub_doc_list：所有sub_doc的列表
3. 构建映射关系：content_id -> [sub_doc_id, ...]（使用列表索引+1作为ID）
"""

import json
from typing import List, Dict, Any


class ContentMappingBuilder:
    """内容映射构建器（简化版）"""
    
    def __init__(self):
        self.content_list = []  # 所有content的列表（字典列表）
        self.sub_doc_list = []  # 所有sub_doc的列表（字典列表）
        self.mapping = {}  # content_idx -> [sub_doc_idx, ...] 的映射
        self.content2idx = {}  # content -> content_idx 的映射
        
        # 用于去重
        self._content_set = set()
        self._sub_doc_content2idx = {}  # sub_doc内容的JSON字符串 -> sub_doc_idx的映射，用于去重
    
    def _dict_to_key(self, d: Dict[str, Any]) -> str:
        """将字典转换为可哈希的key（用于去重）"""
        import json
        return json.dumps(d, ensure_ascii=False, sort_keys=True)
        
    def add_fault_file_data(self, fault_file_data: List[Dict[str, Any]], sub_doc_id_to_content: Dict[Any, Dict[str, Any]] = None):
        """
        添加故障类文件数据
        
        Args:
            fault_file_data: [{"content": {"title": "", "content": ""}, "sub_doc_id": [xx, xx]}, ...]
            sub_doc_id_to_content: {sub_doc_id: {"title": "", "content": ""}} 映射字典（可选）
        """
        for item in fault_file_data:
            content = item.get("content", {})
            sub_doc_ids = item.get("sub_doc_id", [])
            
            content_key = self._dict_to_key(content)
            if content_key in self._content_set:
                continue
            
            self.content_list.append(content)
            self._content_set.add(content_key)
            content_idx = len(self.content_list)
            self.content2idx[content_key] = content_idx
            
            mapped_sub_doc_idxs = []
            for sub_doc_id in sub_doc_ids:
                if sub_doc_id_to_content and sub_doc_id in sub_doc_id_to_content:
                    sub_doc_content = sub_doc_id_to_content[sub_doc_id]
                else:
                    sub_doc_content = {"title": str(sub_doc_id), "content": str(sub_doc_id)}
                
                sub_doc_key = self._dict_to_key(sub_doc_content)
                if sub_doc_key in self._sub_doc_content2idx:
                    sub_doc_idx = self._sub_doc_content2idx[sub_doc_key]
                else:
                    self.sub_doc_list.append(sub_doc_content)
                    sub_doc_idx = len(self.sub_doc_list)
                    self._sub_doc_content2idx[sub_doc_key] = sub_doc_idx
                
                mapped_sub_doc_idxs.append(sub_doc_idx)
            
            self.mapping[content_idx] = mapped_sub_doc_idxs
    
    def add_function_file_data(self, function_file_data: List[Dict[str, Any]], sub_doc_id_to_content: Dict[Any, Dict[str, Any]] = None):
        """
        添加功能类文件数据
        
        Args:
            function_file_data: [{"content": {"title": "", "content": ""}, "sub_doc_id": [xx, xx]}, ...]
            sub_doc_id_to_content: {sub_doc_id: {"title": "", "content": ""}} 映射字典（可选）
        """
        for item in function_file_data:
            content = item.get("content", {})
            sub_doc_ids = item.get("sub_doc_id", [])
            
            content_key = self._dict_to_key(content)
            if content_key in self._content_set:
                continue
            
            self.content_list.append(content)
            self._content_set.add(content_key)
            content_idx = len(self.content_list)
            self.content2idx[content_key] = content_idx
            
            mapped_sub_doc_idxs = []
            for sub_doc_id in sub_doc_ids:
                if sub_doc_id_to_content and sub_doc_id in sub_doc_id_to_content:
                    sub_doc_content = sub_doc_id_to_content[sub_doc_id]
                else:
                    sub_doc_content = {"title": str(sub_doc_id), "content": str(sub_doc_id)}
                
                sub_doc_key = self._dict_to_key(sub_doc_content)
                if sub_doc_key in self._sub_doc_content2idx:
                    sub_doc_idx = self._sub_doc_content2idx[sub_doc_key]
                else:
                    self.sub_doc_list.append(sub_doc_content)
                    sub_doc_idx = len(self.sub_doc_list)
                    self._sub_doc_content2idx[sub_doc_key] = sub_doc_idx
                
                mapped_sub_doc_idxs.append(sub_doc_idx)
            
            self.mapping[content_idx] = mapped_sub_doc_idxs
    
    def add_common_file_data(self, common_file_data: List[Dict[str, Any]], sub_doc_id_to_content: Dict[Any, Dict[str, Any]] = None):
        """
        添加通用类文件数据
        
        Args:
            common_file_data: [{"content": {"title": "", "content": ""}, "sub_doc_id": [xx, xx]}, ...]
            sub_doc_id_to_content: {sub_doc_id: {"title": "", "content": ""}} 映射字典（可选）
        """
        for item in common_file_data:
            content = item.get("content", {})
            sub_doc_ids = item.get("sub_doc_id", [])
            
            content_key = self._dict_to_key(content)
            if content_key in self._content_set:
                continue
            
            self.content_list.append(content)
            self._content_set.add(content_key)
            content_idx = len(self.content_list)
            self.content2idx[content_key] = content_idx
            
            mapped_sub_doc_idxs = []
            for sub_doc_id in sub_doc_ids:
                if sub_doc_id_to_content and sub_doc_id in sub_doc_id_to_content:
                    sub_doc_content = sub_doc_id_to_content[sub_doc_id]
                else:
                    sub_doc_content = {"title": str(sub_doc_id), "content": str(sub_doc_id)}
                
                sub_doc_key = self._dict_to_key(sub_doc_content)
                if sub_doc_key in self._sub_doc_content2idx:
                    sub_doc_idx = self._sub_doc_content2idx[sub_doc_key]
                else:
                    self.sub_doc_list.append(sub_doc_content)
                    sub_doc_idx = len(self.sub_doc_list)
                    self._sub_doc_content2idx[sub_doc_key] = sub_doc_idx
                
                mapped_sub_doc_idxs.append(sub_doc_idx)
            
            self.mapping[content_idx] = mapped_sub_doc_idxs
    
    def add_pgindex_data(self, pgindex_data: List[Dict[str, Any]]):
        """
        添加pgindex数据
        
        Args:
            pgindex_data: [{"title": "", "content": ""}, ...]
        """
        for content in pgindex_data:
            content_key = self._dict_to_key(content)
            if content_key in self._content_set:
                continue
            
            self.content_list.append(content)
            self._content_set.add(content_key)
            content_idx = len(self.content_list)
            self.content2idx[content_key] = content_idx
            
            # pgindex的content渲染块就是自己
            sub_doc_key = content_key
            if sub_doc_key in self._sub_doc_content2idx:
                sub_doc_idx = self._sub_doc_content2idx[sub_doc_key]
            else:
                self.sub_doc_list.append(content)
                sub_doc_idx = len(self.sub_doc_list)
                self._sub_doc_content2idx[sub_doc_key] = sub_doc_idx
            
            self.mapping[content_idx] = [sub_doc_idx]
    
    def get_content_list(self) -> List[str]:
        """获取content列表"""
        return self.content_list.copy()
    
    def get_sub_doc_list(self) -> List[Any]:
        """获取sub_doc列表"""
        return self.sub_doc_list.copy()
    
    def get_mapping(self) -> Dict[int, List[int]]:
        """获取映射关系：content_idx -> [sub_doc_idx, ...]（索引从1开始）"""
        return self.mapping.copy()
    
    def get_content2idx(self) -> Dict[str, int]:
        """获取content到索引的映射：content -> content_idx"""
        return self.content2idx.copy()
    
    def export_to_dict(self) -> Dict[str, Any]:
        """导出所有数据为字典"""
        return {
            "content_list": self.content_list,
            "sub_doc_list": self.sub_doc_list,
            "mapping": self.mapping,
            "content2idx": self.content2idx
        }
    
    def save_to_json(self, filepath: str):
        """保存到JSON文件"""
        data = self.export_to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"映射已保存到: {filepath}")


def main():
    """测试示例"""
    
    # 模拟故障类文件数据
    fault_file_data = [
        {"content": {"title": "故障1", "content": "变频器MD630过流故障"}, "sub_doc_id": [101, 102]},
        {"content": {"title": "故障2", "content": "变频器MD605过压故障"}, "sub_doc_id": [201, 202]},
    ]
    
    # 模拟功能类文件数据
    function_file_data = [
        {"content": {"title": "功能1", "content": "变频器MD630的参数配置功能"}, "sub_doc_id": [301, 302, 303]},
    ]
    
    # 模拟通用类文件数据
    common_file_data = [
        {"content": {"title": "通用1", "content": "变频器安装注意事项"}, "sub_doc_id": [401]},
    ]
    
    # sub_doc_id 到实际内容的映射（三类共用）
    sub_doc_id_to_content = {
        101: {"title": "故障原因", "content": "MD630过流故障章节1：故障原因"},
        102: {"title": "解决方法", "content": "MD630过流故障章节2：解决方法"},
        201: {"title": "故障原因", "content": "MD605过压故障章节1：故障原因"},
        202: {"title": "解决方法", "content": "MD605过压故障章节2：解决方法"},
        301: {"title": "基础参数", "content": "MD630参数配置章节1：基础参数"},
        302: {"title": "高级参数", "content": "MD630参数配置章节2：高级参数"},
        303: {"title": "通讯参数", "content": "MD630参数配置章节3：通讯参数"},
        401: {"title": "安装指南", "content": "变频器安装：物理安装指南"}
    }
    
    # 模拟pgindex数据（content本身就是sub_doc）
    pgindex_data = [
        {"title": "原理", "content": "变频器基本原理介绍"},
        {"title": "问答", "content": "变频器常见问题解答"},
        {"title": "维护", "content": "变频器维护保养指南"}
    ]
    
    # 创建映射构建器
    builder = ContentMappingBuilder()
    
    # 添加三类文件1数据
    print("=== 添加故障类文件数据 ===")
    builder.add_fault_file_data(fault_file_data, sub_doc_id_to_content)
    
    print("=== 添加功能类文件数据 ===")
    builder.add_function_file_data(function_file_data, sub_doc_id_to_content)
    
    print("=== 添加通用类文件数据 ===")
    builder.add_common_file_data(common_file_data, sub_doc_id_to_content)
    
    print("=== 添加pgindex数据 ===")
    builder.add_pgindex_data(pgindex_data)
    
    # 获取结果
    content_list = builder.get_content_list()
    sub_doc_list = builder.get_sub_doc_list()
    mapping = builder.get_mapping()
    content2idx = builder.get_content2idx()
    
    print("\n=== Content列表（索引从1开始）===")
    for i, content in enumerate(content_list, 1):
        print(f"[{i}] {content}")
    
    print("\n=== Sub Doc列表（索引从1开始）===")
    for i, sub_doc in enumerate(sub_doc_list, 1):
        print(f"[{i}] {sub_doc}")
    
    print("\n=== 映射关系：Content索引 -> Sub Doc索引 ===")
    for content_idx, sub_doc_idxs in mapping.items():
        content = content_list[content_idx - 1]
        print(f"\nContent [{content_idx}]: {content}")
        print(f"  -> Sub Doc索引: {sub_doc_idxs}")
        for sub_doc_idx in sub_doc_idxs:
            sub_doc = sub_doc_list[sub_doc_idx - 1]
            print(f"     [{sub_doc_idx}] {sub_doc}")
    
    # 导出数据
    print("\n=== 导出到JSON ===")
    builder.save_to_json("content_mapping.json")
    
    print("\n=== Content到索引的映射（content2idx）===")
    for content, idx in content2idx.items():
        print(f"{content} -> [{idx}]")
    
    print("\n=== 统计信息 ===")
    print(f"Content总数: {len(content_list)}")
    print(f"Sub Doc总数: {len(sub_doc_list)}")


if __name__ == '__main__':
    main()
