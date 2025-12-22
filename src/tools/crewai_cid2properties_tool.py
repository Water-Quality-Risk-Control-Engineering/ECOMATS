import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.cid2properties_tool import get_cid2properties_tool

class CID2PropertiesToolInput(BaseModel):
    """CID2Properties Tool Input Model"""
    cid: str = Field(description="PubChem Compound ID (CID)")

class CrewAICID2PropertiesTool(BaseTool):
    """CrewAI tool wrapper for querying properties by PubChem CID"""
    
    name: str = "CID to Properties Lookup"
    description: str = (
        "Query compound properties by PubChem Compound ID (CID). "
        "Get molecular structure, physicochemical properties, and bioactivity. "
        "Use when you need detailed compound info from a known CID."
    )
    args_schema: type[BaseModel] = CID2PropertiesToolInput
    
    def _run(self, cid: str) -> str:
        """
        Execute CID to properties query.
        
        Args:
            cid: PubChem Compound ID
            
        Returns:
            JSON formatted query result
        """
        try:
            tool = get_cid2properties_tool()
            result = tool.get_properties_by_cid(cid)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Query error: {str(e)}"}, ensure_ascii=False)