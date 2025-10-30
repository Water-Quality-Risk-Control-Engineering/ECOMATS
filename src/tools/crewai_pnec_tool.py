import json
from typing import Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.pnec_tool import get_pnec_tool

class PNECToolInput(BaseModel):
    """PNEC工具输入参数模型"""
    query: str = Field(description="查询内容（CAS号或化合物名称）")
    query_type: str = Field(default="name", description="查询类型 ('name' 或 'cas')")

class CrewAIPNECTool(BaseTool):
    """CrewAI工具包装器，用于查询化学物质的预测无效应浓度(PNEC)数据"""
    
    name: str = "PNEC Database Query"
    description: str = (
        "查询化学物质的预测无效应浓度(PNEC)数据，用于环境风险评估。"
        "可以基于CAS号或化合物名称查询PNEC值。"
        "当需要评估化学物质的环境安全性时使用此工具。"
    )
    args_schema: type[BaseModel] = PNECToolInput
    
    def _run(self, query: str, query_type: str = "name") -> str:
        """
        执行PNEC数据查询
        
        Args:
            query: 查询内容（CAS号或化合物名称）
            query_type: 查询类型 ("name" 或 "cas")
            
        Returns:
            JSON格式的查询结果
        """
        try:
            # 获取工具实例
            tool = get_pnec_tool()
            
            # 根据查询类型执行相应操作
            if query_type.lower() == "cas":
                result = tool.get_pnec_by_cas(query)
            else:
                result = tool.get_pnec_by_name(query)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行查询时出错: {str(e)}"}, ensure_ascii=False)