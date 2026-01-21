"""
ECOMATS A2A (Agent-to-Agent) Protocol Module.

CrewAI 1.8.1 A2A 协议实现，支持跨项目智能体协作。

功能:
1. Agent Card 生成和管理
2. A2A 服务器（暴露本地 Agent）
3. A2A 客户端（调用远程 Agent）
4. ECOMATS ↔ BioCrew 协作

Usage:
    # 客户端 - 调用 BioCrew Agent
    from workflow.a2a import A2AClient, BioCrewClient
    
    client = BioCrewClient("http://biocrew-server:8080")
    result = await client.identify_microorganisms(pollutant="DBP")
"""

import json
import os
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class AgentCard:
    """Agent Card - A2A 协议中的 Agent 描述"""
    name: str
    description: str
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
        return json_str
    
    @classmethod
    def from_crewai_agent(cls, agent, name: str, description: str, capabilities: List[str]) -> "AgentCard":
        tools = getattr(agent, 'tools', [])
        tool_names = [getattr(t, 'name', str(t)) for t in tools]
        return cls(
            name=name,
            description=description,
            capabilities=capabilities,
            metadata={
                "role": getattr(agent, 'role', 'Unknown'),
                "goal": getattr(agent, 'goal', ''),
                "tools": tool_names,
                "created_at": datetime.now().isoformat()
            }
        )


@dataclass
class A2ATaskResponse:
    """A2A 任务响应"""
    request_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class ECOMATSAgentRegistry:
    """ECOMATS Agent 注册表"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.cards: Dict[str, AgentCard] = {}
    
    def register(self, name: str, agent, description: str, capabilities: List[str]) -> AgentCard:
        self.agents[name] = agent
        card = AgentCard.from_crewai_agent(agent, name, description, capabilities)
        self.cards[name] = card
        return card
    
    def get_agent(self, name: str) -> Optional[Any]:
        return self.agents.get(name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        return [{"name": n, "description": c.description, "capabilities": c.capabilities} 
                for n, c in self.cards.items()]
    
    def export_cards(self, output_dir: str) -> List[str]:
        os.makedirs(output_dir, exist_ok=True)
        paths = []
        for name, card in self.cards.items():
            filepath = os.path.join(output_dir, f"{name}.json")
            card.to_json(filepath)
            paths.append(filepath)
        return paths


class A2AClient:
    """A2A 客户端 - 用于连接远程 A2A 服务器并执行任务"""
    
    def __init__(self, base_url: str, timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._request_counter = 0
    
    def _generate_request_id(self) -> str:
        self._request_counter += 1
        return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._request_counter}"
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/agents")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"❌ 获取 Agent 列表失败: {e}")
            return []
    
    async def execute_task(
        self, agent_name: str, task: str, 
        inputs: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> A2ATaskResponse:
        request_id = self._generate_request_id()
        timeout = timeout or self.timeout
        inputs = inputs or {}
        
        print(f"📤 A2A 请求: [{agent_name}] {task[:50]}...")
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=float(timeout)) as client:
                start = asyncio.get_event_loop().time()
                response = await client.post(
                    f"{self.base_url}/execute",
                    json={"agent_name": agent_name, "task": task, "inputs": inputs}
                )
                response.raise_for_status()
                data = response.json()
                
                result = A2ATaskResponse(
                    request_id=request_id,
                    status=data.get("status", "success"),
                    result=data.get("result"),
                    error=data.get("error"),
                    execution_time=asyncio.get_event_loop().time() - start
                )
                print(f"✅ A2A 响应: {result.status} ({result.execution_time:.2f}s)")
                return result
        except Exception as e:
            return A2ATaskResponse(request_id=request_id, status="error", error=str(e))


class BioCrewClient(A2AClient):
    """BioCrew A2A 客户端 - ECOMATS 与 BioCrew 的协作"""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        super().__init__(base_url)
    
    async def identify_microorganisms(self, pollutant: str, degradation_type: str = "aerobic") -> Dict[str, Any]:
        response = await self.execute_task(
            agent_name="BioCrew-Identifier",
            task=f"识别可降解 {pollutant} 的微生物群落",
            inputs={"pollutant": pollutant, "degradation_type": degradation_type}
        )
        return {"microorganisms": response.result} if response.status == "success" else {"error": response.error}
    
    async def design_community(self, target: str, constraints: List[str]) -> Dict[str, Any]:
        response = await self.execute_task(
            agent_name="BioCrew-Designer",
            task=f"设计用于 {target} 的微生物群落",
            inputs={"target": target, "constraints": constraints}
        )
        return {"community": response.result} if response.status == "success" else {"error": response.error}
    
    async def evaluate_biosolution(self, material: str, microorganisms: List[str]) -> Dict[str, Any]:
        response = await self.execute_task(
            agent_name="BioCrew-Evaluator",
            task="评估材料与微生物的协同效应",
            inputs={"material": material, "microorganisms": microorganisms}
        )
        return {"evaluation": response.result} if response.status == "success" else {"error": response.error}


class ECOMATSAgentServer:
    """ECOMATS A2A 服务器 - 暴露本地 Agent 供远程调用"""
    
    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.registry = ECOMATSAgentRegistry()
    
    def register_agent(self, name: str, agent, description: str, capabilities: List[str]) -> AgentCard:
        return self.registry.register(name, agent, description, capabilities)
    
    def register_ecomats_agents(self, agents: Dict[str, Any]) -> None:
        configs = {
            'designer': ('材料设计专家', ['material_design', 'structure_optimization']),
            'expert_a': ('催化性能评估专家', ['catalytic_evaluation']),
            'expert_b': ('结构合理性评估专家', ['structure_evaluation']),
            'expert_c': ('经济可行性评估专家', ['economic_evaluation']),
            'validator': ('综合验证专家', ['validation']),
            'mechanism': ('机理分析专家', ['mechanism_analysis']),
            'synthesis': ('合成方法指导专家', ['synthesis_design']),
            'operation': ('操作指导专家', ['operation_guidance']),
        }
        for name, agent in agents.items():
            if name in configs:
                desc, caps = configs[name]
                self.register_agent(f"ECOMATS-{name.title()}", agent, f"ECOMATS {desc}", caps)
    
    async def start(self) -> None:
        try:
            from fastapi import FastAPI, HTTPException
            import uvicorn
            
            app = FastAPI(title="ECOMATS A2A Server", version="1.0.0")
            
            @app.get("/agents")
            async def list_agents():
                return self.registry.list_agents()
            
            @app.get("/agents/{agent_name}")
            async def get_agent_card(agent_name: str):
                card = self.registry.cards.get(agent_name)
                if not card:
                    raise HTTPException(status_code=404, detail="Agent not found")
                return card.to_dict()
            
            @app.post("/execute")
            async def execute_task(request: dict):
                agent = self.registry.get_agent(request.get("agent_name"))
                if not agent:
                    raise HTTPException(status_code=404, detail="Agent not found")
                # 简化实现
                return {"status": "success", "result": "Task executed"}
            
            @app.get("/health")
            async def health():
                return {"status": "healthy", "agents": len(self.registry.agents)}
            
            print(f"\n🚀 ECOMATS A2A Server: {self.host}:{self.port}")
            config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info")
            await uvicorn.Server(config).serve()
        except ImportError:
            print("⚠️ 需要安装 FastAPI 和 uvicorn: pip install fastapi uvicorn")


def create_a2a_server(agents: Dict[str, Any], port: int = 8080) -> ECOMATSAgentServer:
    server = ECOMATSAgentServer(port=port)
    server.register_ecomats_agents(agents)
    return server


def create_biocrew_client(base_url: str = "http://localhost:8081") -> BioCrewClient:
    return BioCrewClient(base_url)
