import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.tools.molport_tool import get_molport_tool
from src.utils.context_store import ContextStore

class MolPortAvailabilityInput(BaseModel):
    """MolPort商业可获得性查询输入参数"""
    smiles: str = Field(description="化合物的SMILES字符串")
    similarity_threshold: float = Field(default=0.95, description="相似度阈值（0-1），用于判断是否为可获得，默认0.95")

class MolPortSearchInput(BaseModel):
    """MolPort结构搜索输入参数"""
    smiles: str = Field(description="化合物的SMILES字符串")
    search_type: int = Field(default=4, description="搜索类型：1=子结构，2=超结构，3=精确，4=相似性（默认），5=完美，6=精确片段")
    similarity_index: float = Field(default=0.9, description="相似度阈值（0-1），默认0.9")
    max_results: int = Field(default=100, description="最大返回结果数，默认100（最大10000）")

class MolPortMoleculeInfoInput(BaseModel):
    """MolPort分子详细信息查询输入参数"""
    molecule_id: str = Field(description="MolPort分子ID（如 '2325020' 或 'Molport-002-325-020'）")


class CrewAIMolPortAvailabilityTool(BaseTool):
    """CrewAI工具：检查化合物的商业可获得性"""
    
    name: str = "MolPort Compound Availability Checker"
    description: str = (
        "检查化合物的商业可获得性。通过SMILES字符串查询化合物是否可以从商业供应商购买。"
        "返回可获得性状态、匹配的化合物ID、库存量等信息。"
        "用于评估材料的经济可行性和前驱体的可获得性。"
    )
    args_schema: type[BaseModel] = MolPortAvailabilityInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 3600  # 1小时缓存
    
    def _run(self, smiles: str, similarity_threshold: float = 0.95) -> str:
        """
        检查化合物商业可获得性
        
        Args:
            smiles: 化合物的SMILES字符串
            similarity_threshold: 相似度阈值（0-1）
            
        Returns:
            JSON格式的可获得性评估结果
        """
        try:
            # 检查上下文存储
            cache_key = f"molport_availability:{smiles}:{similarity_threshold}"
            cached_ctx = ContextStore.get(cache_key)
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            
            # 检查内存缓存
            import time as _t
            now = _t.time()
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)
            
            # 执行查询
            tool = get_molport_tool()
            result = tool.check_compound_availability(smiles, similarity_threshold)
            
            # 保存到缓存
            ContextStore.set(cache_key, result)
            self._cache[cache_key] = (now, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"查询时出错: {str(e)}"}, ensure_ascii=False)


class CrewAIMolPortSearchTool(BaseTool):
    """CrewAI工具：MolPort化学结构搜索"""
    
    name: str = "MolPort Chemical Structure Search"
    description: str = (
        "在MolPort数据库中进行化学结构搜索。支持多种搜索模式：精确匹配、相似性搜索、子结构搜索等。"
        "通过SMILES字符串搜索相似或相关的化合物，获取MolPort ID和相似度指数。"
        "用于寻找结构相似的可购买化合物或验证材料设计的可行性。"
    )
    args_schema: type[BaseModel] = MolPortSearchInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 3600
    
    def _run(
        self, 
        smiles: str,
        search_type: int = 4,
        similarity_index: float = 0.9,
        max_results: int = 100
    ) -> str:
        """
        执行化学结构搜索
        
        Args:
            smiles: 化合物的SMILES字符串
            search_type: 搜索类型（1-6）
            similarity_index: 相似度阈值（0-1）
            max_results: 最大返回结果数
            
        Returns:
            JSON格式的搜索结果
        """
        try:
            # 检查上下文存储
            cache_key = f"molport_search:{search_type}:{smiles}:{similarity_index}:{max_results}"
            cached_ctx = ContextStore.get(cache_key)
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            
            # 检查内存缓存
            import time as _t
            now = _t.time()
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)
            
            # 执行查询
            tool = get_molport_tool()
            result = tool.search_by_smiles(
                smiles,
                search_type=search_type,
                similarity_index=similarity_index,
                max_results=max_results
            )
            
            # 保存到缓存
            ContextStore.set(cache_key, result)
            self._cache[cache_key] = (now, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"搜索时出错: {str(e)}"}, ensure_ascii=False)


class CrewAIMolPortMoleculeInfoTool(BaseTool):
    """CrewAI工具：获取MolPort分子详细信息"""
    
    name: str = "MolPort Molecule Info Loader"
    description: str = (
        "通过MolPort ID获取化合物的详细信息，包括SMILES、IUPAC名称、分子式、分子量、"
        "供应商信息、库存量、价格、交货时间等完整的商业化信息。"
        "用于评估特定化合物的商业可获得性和成本。"
    )
    args_schema: type[BaseModel] = MolPortMoleculeInfoInput

    def __init__(self):
        super().__init__()
        self._cache = {}
        self._ttl_seconds = 3600
    
    def _run(self, molecule_id: str) -> str:
        """
        获取分子详细信息
        
        Args:
            molecule_id: MolPort分子ID
            
        Returns:
            JSON格式的分子详细信息
        """
        try:
            # 检查上下文存储
            cache_key = f"molport_molecule:{molecule_id}"
            cached_ctx = ContextStore.get(cache_key)
            if cached_ctx is not None:
                return json.dumps(cached_ctx, ensure_ascii=False, indent=2)
            
            # 检查内存缓存
            import time as _t
            now = _t.time()
            cached = self._cache.get(cache_key)
            if cached and now - cached[0] < self._ttl_seconds:
                return json.dumps(cached[1], ensure_ascii=False, indent=2)
            
            # 执行查询
            tool = get_molport_tool()
            result = tool.get_availability_info(molecule_id)
            
            # 保存到缓存
            ContextStore.set(cache_key, result)
            self._cache[cache_key] = (now, result)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"获取信息时出错: {str(e)}"}, ensure_ascii=False)


# 创建工具实例供智能体使用
molport_availability_tool = CrewAIMolPortAvailabilityTool()
molport_search_tool = CrewAIMolPortSearchTool()
molport_molecule_info_tool = CrewAIMolPortMoleculeInfoTool()
