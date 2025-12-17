"""
PostgreSQL向量数据库查询工具
用于从SFT数据向量数据库中检索相似的问答对
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class PGVectorTool:
    """PostgreSQL向量数据库查询工具"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.host = os.getenv('PG_HOST', '')
        self.port = int(os.getenv('PG_PORT', '5432'))
        self.database = os.getenv('PG_DATABASE', '')
        self.user = os.getenv('PG_USER', '')
        self.password = os.getenv('PG_PASSWORD', '')
        self.table = 'sft_qa_vectors'
        self._conn = None
    
    def _get_connection(self):
        """获取数据库连接"""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        return self._conn
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示
        使用Ollama的qwen3-embedding模型生成1024维向量
        
        Args:
            text: 输入文本
            
        Returns:
            1024维向量列表
        """
        try:
            import requests
            
            # 调用Ollama API生成向量
            response = requests.post(
                'http://localhost:11434/api/embeddings',
                json={
                    'model': 'qwen3-embedding:latest',
                    'prompt': text
                }
            )
            
            if response.status_code == 200:
                return response.json()['embedding']
            else:
                raise Exception(f"Embedding API error: {response.status_code}")
                
        except Exception as e:
            # 如果Ollama不可用，返回零向量
            print(f"Warning: Could not generate embedding: {e}")
            return [0.0] * 1024
    
    def search_similar_qa(
        self,
        query: str,
        agent_type: Optional[str] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        搜索与查询最相似的问答对
        
        Args:
            query: 查询文本
            agent_type: 指定agent类型 ('design_agent', 'synthesis_agent', 'mechanism_agent')
            top_k: 返回结果数量
            similarity_threshold: 相似度阈值 (0-1)
            
        Returns:
            包含相似问答对的字典
        """
        cur = None
        try:
            # 生成查询向量
            query_vector = self._get_embedding(query)
            
            # 构建SQL查询
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # 基础查询
            sql = """
                SELECT 
                    id,
                    agent_type,
                    instruction,
                    output,
                    design,
                    synthesis,
                    mechanism,
                    entities,
                    1 - (instruction_embedding <=> %s::vector) as similarity
                FROM {table}
                WHERE 1 - (instruction_embedding <=> %s::vector) >= %s
            """.format(table=self.table)
            
            params = [query_vector, query_vector, similarity_threshold]
            
            # 如果指定了agent类型，添加过滤条件
            if agent_type:
                sql += " AND agent_type = %s"
                params.append(agent_type)
            
            sql += " ORDER BY instruction_embedding <=> %s::vector LIMIT %s"
            params.extend([query_vector, top_k])
            
            cur.execute(sql, params)
            results = cur.fetchall()
            
            # 格式化结果
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'id': row['id'],
                    'agent_type': row['agent_type'],
                    'instruction': row['instruction'],
                    'output': row['output'],
                    'design': row.get('design'),
                    'synthesis': row.get('synthesis'),
                    'mechanism': row.get('mechanism'),
                    'entities': row.get('entities'),
                    'similarity': float(row['similarity'])
                })
            
            return {
                'success': True,
                'query': query,
                'agent_type': agent_type,
                'total_results': len(formatted_results),
                'results': formatted_results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
        finally:
            if cur:
                cur.close()
    
    def get_by_agent_type(
        self,
        agent_type: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        获取指定agent类型的所有问答对
        
        Args:
            agent_type: agent类型
            limit: 返回数量限制
            
        Returns:
            问答对列表
        """
        cur = None
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute(f"""
                SELECT id, agent_type, instruction, output, design, synthesis, mechanism, entities
                FROM {self.table}
                WHERE agent_type = %s
                LIMIT %s
            """, (agent_type, limit))
            
            results = cur.fetchall()
            
            return {
                'success': True,
                'agent_type': agent_type,
                'total_results': len(results),
                'results': [dict(row) for row in results]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if cur:
                cur.close()
    
    def close(self):
        """关闭数据库连接"""
        if self._conn and not self._conn.closed:
            self._conn.close()


# 创建全局实例
def get_pg_vector_tool() -> PGVectorTool:
    """获取PGVector工具实例"""
    return PGVectorTool()
