"""
PostgreSQL Vector Database Query Tool.
Retrieve similar QA pairs from SFT data vector database.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class PGVectorTool:
    """PostgreSQL Vector Database Query Tool"""
    
    def __init__(self):
        """Initialize database connection"""
        self.host = os.getenv('PG_HOST', '')
        self.port = int(os.getenv('PG_PORT', '5432'))
        self.database = os.getenv('PG_DATABASE', '')
        self.user = os.getenv('PG_USER', '')
        self.password = os.getenv('PG_PASSWORD', '')
        self.table = 'sft_qa_vectors'
        self._conn = None
    
    def _get_connection(self):
        """Get database connection"""
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
        Get text vector representation.
        Use Ollama qwen3-embedding model to generate 1024-dim vector.
        
        Args:
            text: Input text
            
        Returns:
            1024-dim vector list
        """
        try:
            import requests
            
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
        Search for most similar QA pairs.
        
        Args:
            query: Query text
            agent_type: Agent type ('design_agent', 'synthesis_agent', 'mechanism_agent')
            top_k: Number of results
            similarity_threshold: Similarity threshold (0-1)
            
        Returns:
            Dict containing similar QA pairs
        """
        cur = None
        try:
            query_vector = self._get_embedding(query)
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
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
            
            if agent_type:
                sql += " AND agent_type = %s"
                params.append(agent_type)
            
            sql += " ORDER BY instruction_embedding <=> %s::vector LIMIT %s"
            params.extend([query_vector, top_k])
            
            cur.execute(sql, params)
            results = cur.fetchall()
            
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
        Get all QA pairs for specified agent type.
        
        Args:
            agent_type: Agent type
            limit: Result limit
            
        Returns:
            QA pair list
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
        """Close database connection"""
        if self._conn and not self._conn.closed:
            self._conn.close()


# Create global instance
def get_pg_vector_tool() -> PGVectorTool:
    """Get PGVector tool instance"""
    return PGVectorTool()
