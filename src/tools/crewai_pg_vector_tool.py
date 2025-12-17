"""
PostgreSQL向量数据库查询工具的CrewAI包装器
用于在CrewAI Agent中调用向量数据库查询功能
"""
import json
from typing import Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.tools.pg_vector_tool import get_pg_vector_tool
from src.utils.context_store import ContextStore


class PGVectorToolInput(BaseModel):
    """PGVector工具输入参数"""
    query: str = Field(description="查询文本，用于语义相似度搜索")
    agent_type: Optional[str] = Field(
        default=None, 
        description="Agent类型过滤: 'design_agent', 'synthesis_agent', 'mechanism_agent'"
    )
    top_k: int = Field(default=3, description="返回结果数量，默认3条")
    similarity_threshold: float = Field(
        default=0.5, 
        description="相似度阈值(0-1)，默认0.5"
    )


class CrewAIPGVectorTool(BaseTool):
    """
    SFT问答对向量数据库查询工具
    
    用于从历史问答对中检索与当前查询最相似的示例，
    帮助Agent生成更准确、更一致的回复。
    
    数据库包含900条水处理材料相关的问答对，
    涵盖设计、合成和机理分析三个领域。
    """
    name: str = "SFT QA Vector Database Query"
    description: str = (
        "查询SFT问答对向量数据库，检索与查询最相似的历史问答示例。"
        "该数据库包含900条水处理材料设计、合成和机理分析的问答对。"
        "输入参数：query(查询文本), agent_type(可选，过滤特定Agent类型), "
        "top_k(返回数量，默认3), similarity_threshold(相似度阈值，默认0.5)。"
        "返回相似问答对列表，包含instruction, output, similarity等字段。"
    )
    args_schema: type[BaseModel] = PGVectorToolInput
    
    def _run(
        self, 
        query: str, 
        agent_type: Optional[str] = None,
        top_k: int = 3,
        similarity_threshold: float = 0.5
    ) -> str:
        """
        执行向量数据库查询
        
        Args:
            query: 查询文本
            agent_type: Agent类型过滤
            top_k: 返回结果数量
            similarity_threshold: 相似度阈值
            
        Returns:
            JSON格式的查询结果
        """
        # 检查缓存
        cache_key = f"pgvector:{query}:{agent_type}:{top_k}:{similarity_threshold}"
        cached_ctx = ContextStore.get(cache_key)
        if cached_ctx is not None:
            return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
        
        try:
            tool = get_pg_vector_tool()
            result = tool.search_similar_qa(
                query=query,
                agent_type=agent_type,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # 缓存结果
            if result.get('success'):
                ContextStore.set(cache_key, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'query': query
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)


# 创建工具实例
pg_vector_tool = CrewAIPGVectorTool()
