"""
CrewAI wrapper for PostgreSQL vector database query tool.
Used for calling vector database query functions in CrewAI Agents.
"""
import json
from typing import Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.tools.pg_vector_tool import get_pg_vector_tool
from src.utils.context_store import ContextStore


class PGVectorToolInput(BaseModel):
    """PGVector Tool Input Model"""
    query: str = Field(description="Query text for semantic similarity search")
    agent_type: Optional[str] = Field(
        default=None, 
        description="Agent type filter: 'design_agent', 'synthesis_agent', 'mechanism_agent'"
    )
    top_k: int = Field(default=3, description="Number of results to return, default 3")
    similarity_threshold: float = Field(
        default=0.5, 
        description="Similarity threshold (0-1), default 0.5"
    )


class CrewAIPGVectorTool(BaseTool):
    """
    SFT QA Vector Database Query Tool.
    
    Retrieves the most similar examples from historical QA pairs for current query,
    helping Agents generate more accurate and consistent responses.
    
    Database contains 900 water treatment material QA pairs,
    covering design, synthesis and mechanism analysis domains.
    """
    name: str = "SFT QA Vector Database Query"
    description: str = (
        "Query SFT QA vector database to retrieve the most similar historical QA examples. "
        "Database contains 900 water treatment material design, synthesis and mechanism QA pairs. "
        "Input: query(text), agent_type(optional filter), top_k(default 3), similarity_threshold(default 0.5). "
        "Returns similar QA pairs with instruction, output, similarity fields."
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
        Execute vector database query.
        
        Args:
            query: Query text
            agent_type: Agent type filter
            top_k: Number of results
            similarity_threshold: Similarity threshold
            
        Returns:
            JSON formatted query result
        """
        # Check cache
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
            
            # Cache result
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


# Create tool instance
pg_vector_tool = CrewAIPGVectorTool()
