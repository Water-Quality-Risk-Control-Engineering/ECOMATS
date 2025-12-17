"""
GDB图数据库查询工具的CrewAI包装器
用于在CrewAI Agent中查询水处理材料知识图谱
"""
import json
from typing import Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from src.tools.gdb_tool import get_gdb_tool
from src.utils.context_store import ContextStore


class GDBCatalystInput(BaseModel):
    """催化剂查询输入参数"""
    catalyst_name: str = Field(
        description="催化剂名称，例如: TiO2, ZnO, Fe3O4, g-C3N4"
    )


class GDBPollutantInput(BaseModel):
    """污染物查询输入参数"""
    pollutant_name: str = Field(
        description="污染物名称，例如: CIP, BPA, Tetracycline, PFOA"
    )


class CrewAIGDBCatalystTool(BaseTool):
    """
    催化剂知识图谱查询工具
    
    用于查询催化剂的降解能力和活性物种生成信息，
    帮助Agent了解催化剂的应用范围和反应机理。
    
    知识图谱包含344种催化剂、15种污染物、10种活性物种，
    以及1713条关系边。
    """
    name: str = "Catalyst Knowledge Graph Query"
    description: str = (
        "查询水处理材料知识图谱，获取催化剂的相关信息。"
        "该图谱包含369个节点和1713条关系，涵盖344种催化剂、15种污染物和10种活性物种。"
        "输入催化剂名称（如TiO2, ZnO），返回该催化剂能降解的污染物列表和生成的活性物种。"
        "适用于：材料设计时了解催化剂应用范围、机理分析时获取反应途径信息。"
    )
    args_schema: type[BaseModel] = GDBCatalystInput
    
    def _run(self, catalyst_name: str) -> str:
        """
        执行催化剂信息查询
        
        Args:
            catalyst_name: 催化剂名称
            
        Returns:
            JSON格式的催化剂完整信息
        """
        # 检查缓存
        cache_key = f"gdb_catalyst:{catalyst_name}"
        cached_ctx = ContextStore.get(cache_key)
        if cached_ctx is not None:
            return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
        
        try:
            tool = get_gdb_tool()
            result = tool.query_catalyst_full_info(catalyst_name)
            
            # 缓存结果
            if result.get('success'):
                ContextStore.set(cache_key, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'catalyst': catalyst_name
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)


class CrewAIGDBPollutantTool(BaseTool):
    """
    污染物降解查询工具
    
    用于查询能够降解特定污染物的催化剂列表，
    帮助Agent进行材料选型和设计决策。
    """
    name: str = "Pollutant Degradation Query"
    description: str = (
        "查询能降解特定污染物的催化剂列表。"
        "支持的污染物包括: CIP, Atrazine, ibuprofen, PFOA, BPA, "
        "Sulfamethoxazole, TC, RhB, 4-NP, MO, Tetracycline, MB, Cr(VI), phenol, OTC。"
        "输入污染物名称，返回能有效降解该污染物的催化剂列表及数量。"
        "适用于：针对特定污染物选择合适的催化剂材料。"
    )
    args_schema: type[BaseModel] = GDBPollutantInput
    
    def _run(self, pollutant_name: str) -> str:
        """
        执行污染物催化剂查询
        
        Args:
            pollutant_name: 污染物名称
            
        Returns:
            JSON格式的催化剂列表
        """
        # 检查缓存
        cache_key = f"gdb_pollutant:{pollutant_name}"
        cached_ctx = ContextStore.get(cache_key)
        if cached_ctx is not None:
            return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
        
        try:
            tool = get_gdb_tool()
            result = tool.query_pollutant_catalysts(pollutant_name)
            
            # 缓存结果
            if result.get('success'):
                ContextStore.set(cache_key, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'pollutant': pollutant_name
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)


# 创建工具实例
gdb_catalyst_tool = CrewAIGDBCatalystTool()
gdb_pollutant_tool = CrewAIGDBPollutantTool()
