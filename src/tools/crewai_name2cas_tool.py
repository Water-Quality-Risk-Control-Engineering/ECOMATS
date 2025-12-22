import json
from crewai.tools import BaseTool
from src.tools.name2cas_tool import get_name2cas_tool

class CrewAIName2CASTool(BaseTool):
    """CrewAI tool wrapper for converting material names to CAS numbers"""
    
    name: str = "Name to CAS Number Converter"
    description: str = (
        "Convert chemical substance names to CAS registry numbers. "
        "Use when you need to obtain the unique identifier of a compound. "
        "Input parameter is the name of the chemical substance."
    )
    
    def _run(self, compound_name: str) -> str:
        """
        Execute name to CAS number conversion.
        
        Args:
            compound_name: Chemical substance name
            
        Returns:
            JSON formatted conversion result
        """
        try:
            tool = get_name2cas_tool()
            result = tool.convert_name_to_cas(compound_name)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Conversion error: {str(e)}"}, ensure_ascii=False)