import logging
from src.agents.base_agent import BaseAgent
from crewai import Agent
from src.utils.prompt_loader import load_prompt
from src.tools import materials_project_tool, pubchem_tool, name2cas_tool, name2properties_tool, formula2properties_tool, material_search_tool, cid2properties_tool, pnec_tool

# Configure logging
# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Material Design Expert class / 材料设计专家类
class CreativeDesigningAgent(BaseAgent):
    """Creative Designing Agent for water treatment materials"""
    
    def __init__(self, llm):
        """
        Initialize the Creative Designing Agent
        
        Args:
            llm: The language model instance
        """
        from src.config.config import Config
        super().__init__(
            llm=llm,
            role="Creative_Designing_agent",  # Material Design Expert
            goal="设计和优化水处理材料方案",  # Design and optimize water treatment material solutions
            prompt_file="material_designer_prompt.md",
            temperature=Config.MATERIAL_DESIGNER_TEMPERATURE
        )
    
    def create_agent(self):
        """
        Create the agent instance with appropriate tools
        
        Returns:
            Agent: Configured agent instance with tools attached
        """
        # Try to create EAS model instance
        # 尝试创建EAS模型实例
        try:
            from src.utils.llm_config import create_eas_llm
            eas_llm = create_eas_llm()
            logger.info("Successfully created EAS LLM instance")
            # 更新llm属性以使用EAS
            self.llm = eas_llm
        except Exception as e:
            logger.error(f"Failed to create EAS model instance: {e}")
            # 如果EAS配置失败，则使用传入的LLM
            # Keep self.llm as is
        
        agent = super().create_agent()
        # Add chemical database query tools for the material design expert
        # 为材料设计专家添加化学数据库查询工具
        agent.tools = [
            materials_project_tool,      # Materials Project database tool
            pubchem_tool,                # PubChem database tool  
            name2cas_tool,               # Chemical name to CAS number lookup
            name2properties_tool,        # Chemical name to properties lookup
            cid2properties_tool,         # CID to properties lookup
            formula2properties_tool,     # Chemical formula to properties lookup
            material_search_tool,        # General material search tool
            pnec_tool                    # PNEC tool
        ]
        return agent

# 创建实例
material_designer_instance = None

def get_material_designer(llm=None):
    global material_designer_instance
    if material_designer_instance is None and llm is not None:
        material_designer_instance = CreativeDesigningAgent(llm).create_agent()
    return material_designer_instance

# 兼容旧版本的直接访问方式
material_designer = None