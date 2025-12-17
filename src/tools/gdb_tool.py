"""
阿里云GDB图数据库查询工具
用于查询水处理材料知识图谱
"""
from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
import json
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class GDBTool:
    """阿里云GDB图数据库查询工具"""
    
    def __init__(self):
        """初始化GDB连接"""
        self.host = os.getenv('GDB_HOST', '')
        self.port = int(os.getenv('GDB_PORT', '3734'))
        self.username = os.getenv('GDB_USERNAME', '')
        self.password = os.getenv('GDB_PASSWORD', '')
        self.graph = 'g'
        self._client = None
    
    def _get_client(self):
        """获取Gremlin客户端"""
        if self._client is None:
            url = f"ws://{self.host}:{self.port}/gremlin"
            self._client = client.Client(
                url,
                self.graph,
                username=self.username,
                password=self.password,
                message_serializer=serializer.GraphSONSerializersV3d0()
            )
        return self._client
    
    def query_catalyst_degradation(
        self,
        catalyst_name: str
    ) -> Dict[str, Any]:
        """
        查询某催化剂能降解的污染物
        
        Args:
            catalyst_name: 催化剂名称 (例如: SO4, H2O2, TiO2)
            
        Returns:
            包含污染物列表的字典
        """
        try:
            c = self._get_client()
            
            # 查询降解关系
            query = f"""
                g.V().has('Catalyst', 'name', '{catalyst_name}')
                 .out('DEGRADES')
                 .values('name')
            """
            
            result = c.submit(query).all().result()
            pollutants = list(result) if result else []
            
            return {
                'success': True,
                'catalyst': catalyst_name,
                'pollutants': pollutants,
                'count': len(pollutants)
            }
            
        except GremlinServerError as e:
            return {
                'success': False,
                'error': f"GDB查询错误: {str(e)}",
                'catalyst': catalyst_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'catalyst': catalyst_name
            }
    
    def query_catalyst_active_species(
        self,
        catalyst_name: str
    ) -> Dict[str, Any]:
        """
        查询某催化剂生成的活性物种
        
        Args:
            catalyst_name: 催化剂名称
            
        Returns:
            包含活性物种列表的字典
        """
        try:
            c = self._get_client()
            
            query = f"""
                g.V().has('Catalyst', 'name', '{catalyst_name}')
                 .out('GENERATES')
                 .values('name')
            """
            
            result = c.submit(query).all().result()
            species = list(result) if result else []
            
            return {
                'success': True,
                'catalyst': catalyst_name,
                'active_species': species,
                'count': len(species)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'catalyst': catalyst_name
            }
    
    def query_pollutant_catalysts(
        self,
        pollutant_name: str
    ) -> Dict[str, Any]:
        """
        查询能降解某污染物的催化剂
        
        Args:
            pollutant_name: 污染物名称 (例如: CIP, BPA, Tetracycline)
            
        Returns:
            包含催化剂列表的字典
        """
        try:
            c = self._get_client()
            
            query = f"""
                g.V().has('Pollutant', 'name', '{pollutant_name}')
                 .in('DEGRADES')
                 .values('name')
            """
            
            result = c.submit(query).all().result()
            catalysts = list(result) if result else []
            
            return {
                'success': True,
                'pollutant': pollutant_name,
                'catalysts': catalysts,
                'count': len(catalysts)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pollutant': pollutant_name
            }
    
    def query_catalyst_full_info(
        self,
        catalyst_name: str
    ) -> Dict[str, Any]:
        """
        查询催化剂的完整信息（降解的污染物 + 生成的活性物种）
        
        Args:
            catalyst_name: 催化剂名称
            
        Returns:
            包含完整信息的字典
        """
        try:
            degradation = self.query_catalyst_degradation(catalyst_name)
            species = self.query_catalyst_active_species(catalyst_name)
            
            if degradation['success'] and species['success']:
                return {
                    'success': True,
                    'catalyst': catalyst_name,
                    'degrades_pollutants': degradation['pollutants'],
                    'generates_species': species['active_species'],
                    'total_pollutants': degradation['count'],
                    'total_species': species['count']
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to query complete information',
                    'catalyst': catalyst_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'catalyst': catalyst_name
            }
    
    def get_all_pollutants(self) -> Dict[str, Any]:
        """获取所有污染物列表"""
        try:
            c = self._get_client()
            query = "g.V().hasLabel('Pollutant').values('name')"
            result = c.submit(query).all().result()
            
            return {
                'success': True,
                'pollutants': list(result) if result else [],
                'count': len(result) if result else 0
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_all_active_species(self) -> Dict[str, Any]:
        """获取所有活性物种列表"""
        try:
            c = self._get_client()
            query = "g.V().hasLabel('ActiveSpecies').values('name')"
            result = c.submit(query).all().result()
            
            return {
                'success': True,
                'active_species': list(result) if result else [],
                'count': len(result) if result else 0
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_top_catalysts(self, top_k: int = 10) -> Dict[str, Any]:
        """获取连接度最高的催化剂"""
        try:
            c = self._get_client()
            query = f"""
                g.V().hasLabel('Catalyst')
                 .project('name', 'degree')
                 .by('name')
                 .by(bothE().count())
                 .order().by(select('degree'), desc)
                 .limit({top_k})
            """
            result = c.submit(query).all().result()
            
            catalysts = []
            if result:
                for item in result:
                    catalysts.append({
                        'name': item['name'],
                        'connections': item['degree']
                    })
            
            return {
                'success': True,
                'top_catalysts': catalysts,
                'count': len(catalysts)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def close(self):
        """关闭客户端连接"""
        if self._client:
            self._client.close()
            self._client = None


# 创建全局实例
def get_gdb_tool() -> GDBTool:
    """获取GDB工具实例"""
    return GDBTool()
