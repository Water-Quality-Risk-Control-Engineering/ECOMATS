import json
from typing import Optional
from crewai.tools import BaseTool
from tools.formula2properties_tool import get_formula2properties_tool

class CrewAIFormula2PropertiesTool(BaseTool):
    """CrewAI工具包装器，用于根据化学式预测性质"""
    
    name: str = "Formula to Properties Predictor"
    description: str = (
        "根据化学分子式预测化合物的物理化学性质。"
        "可以预测分子量、晶体结构、能带隙等信息。"
        "当需要基于化学式了解可能的材料性质时使用此工具。"
    )
    
    def _run(self, formula: str) -> str:
        """
        执行化学式到性质的预测
        
        Args:
            formula: 化学分子式
            
        Returns:
            JSON格式的预测结果
        """
        try:
            # 获取工具实例
            tool = get_formula2properties_tool()
            
            # 执行预测
            result = tool.get_properties_by_formula(formula)
            
            # 返回JSON格式的结果
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"执行预测时出错: {str(e)}"}, ensure_ascii=False)