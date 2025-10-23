#!/usr/bin/env python3
"""
使用ECOMATS系统生成催化PMS活化的催化剂材料的高级脚本
"""

import json
import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from src.config.config import Config
import dashscope

# 导入ECOMATS系统的组件
from src.agents.Creative_Designing_agent import CreativeDesigningAgent
from src.agents.Assessment_Screening_agent_A import AssessmentScreeningAgentA
from src.agents.Assessment_Screening_agent_B import AssessmentScreeningAgentB
from src.agents.Assessment_Screening_agent_C import AssessmentScreeningAgentC
from src.agents.Assessment_Screening_agent_Overall import AssessmentScreeningAgentOverall
from src.agents.Mechanism_Mining_agent import MechanismMiningAgent
from src.agents.Synthesis_Guiding_agent import SynthesisGuidingAgent
from src.agents.Operation_Suggesting_agent import OperationSuggestingAgent

from src.tasks.design_task import DesignTask
from src.tasks.evaluation_task import EvaluationTask
from src.tasks.final_validation_task import FinalValidationTask
from src.tasks.mechanism_analysis_task import MechanismAnalysisTask
from src.tasks.synthesis_method_task import SynthesisMethodTask
from src.tasks.operation_suggesting_task import OperationSuggestingTask

def create_ecomats_crew(target_pollutant="全氟辛酸(PFOA)"):
    """创建ECOMATS系统Crew"""
    
    # 设置dashscope的API密钥
    dashscope.api_key = Config.QWEN_API_KEY
    
    # 初始化LLM模型
    llm = ChatOpenAI(
        base_url=Config.OPENAI_API_BASE,
        api_key=Config.OPENAI_API_KEY,
        model="openai/" + Config.QWEN_MODEL_NAME,
        temperature=Config.MODEL_TEMPERATURE,
        streaming=False,
        max_tokens=Config.MODEL_MAX_TOKENS
    )
    
    # 创建智能体
    material_designer = CreativeDesigningAgent(llm).create_agent()
    expert_a = AssessmentScreeningAgentA(llm).create_agent()
    expert_b = AssessmentScreeningAgentB(llm).create_agent()
    expert_c = AssessmentScreeningAgentC(llm).create_agent()
    final_validator = AssessmentScreeningAgentOverall(llm).create_agent()
    mechanism_expert = MechanismMiningAgent(llm).create_agent()
    synthesis_expert = SynthesisGuidingAgent(llm).create_agent()
    operation_suggesting = OperationSuggestingAgent(llm).create_agent()
    
    # 创建任务
    design_task = DesignTask(llm).create_task(
        material_designer, 
        user_requirement=f"设计一种用于催化过一硫酸盐(PMS)活化降解{target_pollutant}的高效催化剂"
    )
    
    evaluation_task_a = EvaluationTask(llm).create_task(expert_a, design_task)
    evaluation_task_b = EvaluationTask(llm).create_task(expert_b, design_task)
    evaluation_task_c = EvaluationTask(llm).create_task(expert_c, design_task)
    
    final_validation_task = FinalValidationTask(llm).create_task(
        final_validator, 
        [design_task, evaluation_task_a, evaluation_task_b, evaluation_task_c]
    )
    
    mechanism_analysis_task = MechanismAnalysisTask(llm).create_task(mechanism_expert, final_validation_task)
    synthesis_method_task = SynthesisMethodTask(llm).create_task(synthesis_expert, final_validation_task)
    operation_suggesting_task = OperationSuggestingTask(llm).create_task(operation_suggesting, final_validation_task)
    
    # 创建Crew
    ecomats_crew = Crew(
        agents=[
            material_designer,
            expert_a,
            expert_b,
            expert_c,
            final_validator,
            mechanism_expert,
            synthesis_expert,
            operation_suggesting
        ],
        tasks=[
            design_task,
            evaluation_task_a,
            evaluation_task_b,
            evaluation_task_c,
            final_validation_task,
            mechanism_analysis_task,
            synthesis_method_task,
            operation_suggesting_task
        ],
        process=Process.sequential,
        verbose=Config.VERBOSE
    )
    
    return ecomats_crew

def run_ecomats_design(target_pollutant="全氟辛酸(PFOA)"):
    """运行ECOMATS设计流程"""
    print(f"开始设计用于降解{target_pollutant}的PMS活化催化剂...")
    
    # 创建Crew
    crew = create_ecomats_crew(target_pollutant)
    
    # 执行
    result = crew.kickoff()
    
    return result

def parse_and_display_results(result):
    """解析并显示结果"""
    try:
        # 尝试解析JSON结果
        if isinstance(result, str):
            result_data = json.loads(result)
        else:
            result_data = result
            
        print("\n" + "="*60)
        print("ECOMATS系统设计结果")
        print("="*60)
        
        # 显示材料设计方案
        if "designer" in result_data and result_data["designer"] == "Material Designer":
            print("\n【材料设计方案】")
            for i, design in enumerate(result_data["designs"], 1):
                print(f"\n{i}. {design['name']}")
                print(f"   类型: {design['type']}")
                print(f"   化学式: {design['chemical_formula']}")
                print(f"   结构特征: {design['structural_features']}")
                print(f"   设计原理: {design['design_rationale']}")
                print(f"   性能预测: {design['performance_projections']}")
                print(f"   合成可行性: {design['synthesis_feasibility']}")
                
        # 显示评估结果
        elif "evaluator" in result_data:
            if result_data["evaluator"] in ["A", "B", "C"]:
                print(f"\n【评估专家{result_data['evaluator']}评估结果】")
                for result_item in result_data["results"]:
                    print(f"   评分: {result_item['scores']}")
                    print(f"   优点: {result_item['pros']}")
                    print(f"   缺点: {result_item['cons']}")
                    
            elif result_data["evaluator"] == "Final Validator":
                print("\n【最终验证结果】")
                for result_item in result_data["results"]:
                    print(f"   材料名称: {result_item['name']}")
                    print(f"   专家评分: {result_item['expert_scores']}")
                    print(f"   平均分: {result_item['average_scores']}")
                    print(f"   加权总分: {result_item['weighted_total']}")
                    print(f"   最终排名: {result_item['rank']}")
                    print(f"   优点: {result_item['pros']}")
                    print(f"   缺点: {result_item['cons']}")
                    print(f"   一致性分析: {result_item['expert_consistency']}")
                    print(f"   改进建议: {result_item['recommendations']}")
                    
        # 显示机理分析结果
        elif "expert" in result_data and result_data["expert"] == "Mechanism Expert":
            print("\n【机理分析结果】")
            for analysis in result_data["analysis"]:
                print(f"   材料: {analysis['material']}")
                print(f"   机理: {analysis['mechanism']}")
                print(f"   构效关系: {analysis['structure_property_relationship']}")
                print(f"   优化建议: {analysis['optimization_suggestions']}")
                print(f"   性能预测: {analysis['performance_prediction']}")
                
        # 显示合成方法结果
        elif "expert" in result_data and result_data["expert"] == "Synthesis Expert":
            print("\n【合成方法设计】")
            for protocol in result_data["synthesis_protocols"]:
                print(f"   材料名称: {protocol['material_name']}")
                print(f"   化学式: {protocol['chemical_formula']}")
                print(f"   目标产量: {protocol['target_amount']}")
                print(f"   合成方法: {protocol['synthesis_method']}")
                print("   前驱体溶液:")
                for component in protocol['precursor_solution']['components']:
                    print(f"     - {component['reagent']}: {component['concentration']}, {component['volume']}")
                print("   合成步骤:")
                for step, description in protocol['synthesis_protocol'].items():
                    print(f"     {step}: {description}")
                print("   关键参数:")
                for param, value in protocol['key_parameters'].items():
                    print(f"     {param}: {value}")
                    
        # 显示操作建议结果
        elif "expert" in result_data and result_data["expert"] == "Operation Suggesting Agent":
            print("\n【操作建议】")
            for guidance in result_data["operational_guidance"]:
                print(f"   过程概述: {guidance['process_overview']}")
                print("   详细步骤:")
                for step in guidance['detailed_steps']:
                    print(f"     步骤 {step['step_number']}: {step['description']}")
                    for param, value in step['critical_parameters'].items():
                        print(f"       {param}: {value}")
                print("   质量控制:")
                for method in guidance['quality_control']['testing_methods']:
                    print(f"     - {method}")
                print("   故障排除:")
                for issue in guidance['troubleshooting']:
                    print(f"     问题: {issue['issue']}")
                    print(f"     解决方案: {issue['solution']}")
                print("   安全注意事项:")
                for note in guidance['safety_notes']:
                    print(f"     - {note}")
                    
    except json.JSONDecodeError:
        print("无法解析JSON格式的结果:")
        print(result)
    except Exception as e:
        print(f"解析结果时出错: {e}")
        print("原始结果:")
        print(result)

def main():
    """主函数"""
    print("ECOMATS高级催化剂设计系统")
    print("="*50)
    
    # 验证API密钥
    if not Config.is_api_key_valid(Config.QWEN_API_KEY):
        print("错误：API密钥未正确设置")
        return
    
    # 获取目标污染物
    target_pollutant = input("请输入目标污染物 (默认: 全氟辛酸(PFOA)): ").strip()
    if not target_pollutant:
        target_pollutant = "全氟辛酸(PFOA)"
    
    # 运行设计
    result = run_ecomats_design(target_pollutant)
    
    # 显示结果
    parse_and_display_results(result)
    
    # 保存结果到文件
    try:
        with open("catalyst_design_results.json", "w", encoding="utf-8") as f:
            if isinstance(result, str):
                f.write(result)
            else:
                json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到 catalyst_design_results.json 文件中")
    except Exception as e:
        print(f"保存结果时出错: {e}")

if __name__ == "__main__":
    main()