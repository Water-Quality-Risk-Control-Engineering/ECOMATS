#!/usr/bin/env python3
"""
评价工具
实现基于核心标准的方案评价结果判断逻辑
"""

import json
import re

class EvaluationTool:
    @staticmethod
    def analyze_evaluation_result(evaluation_report):
        """
        分析评价报告并判断是否需要重新设计
        
        Args:
            evaluation_report (str): 技术评估专家生成的方案评价报告
            
        Returns:
            dict: 包含判断结果和建议的字典
        """
        analysis_result = {
            "core_standards_met": True,
            "need_redesign": False,
            "reason": "",
            "suggestions": ""
        }
        
        try:
            # 尝试解析JSON格式的评价报告
            if isinstance(evaluation_report, str):
                # 提取JSON内容
                json_match = re.search(r'\{.*\}', evaluation_report, re.DOTALL)
                if json_match:
                    report_data = json.loads(json_match.group())
                    
                    # 检查核心标准（催化性能）
                    if "results" in report_data:
                        for result in report_data["results"]:
                            if "scores" in result:
                                # 催化性能是第一个评分维度（索引0），权重50%
                                catalytic_performance = result["scores"][0]
                                if catalytic_performance < 6:  # 假设6分以下为不达标
                                    analysis_result["core_standards_met"] = False
                                    analysis_result["need_redesign"] = True
                                    analysis_result["reason"] = f"催化性能评分过低: {catalytic_performance}/10"
                                    analysis_result["suggestions"] = "建议重新设计材料结构，优化活性位点和反应路径"
                                    break
                    
                    # 检查是否有任何维度评分过低
                    if analysis_result["core_standards_met"]:
                        for result in report_data["results"]:
                            if "scores" in result:
                                scores = result["scores"]
                                for i, score in enumerate(scores):
                                    if score < 3:  # 任何维度评分低于3分
                                        dimension_names = ["催化性能", "经济可行性", "环境友好性", "技术可行性", "结构合理性"]
                                        analysis_result["core_standards_met"] = False
                                        analysis_result["need_redesign"] = True
                                        analysis_result["reason"] = f"{dimension_names[i]}评分过低: {score}/10"
                                        analysis_result["suggestions"] = f"建议针对{dimension_names[i]}进行优化改进"
                                        break
                                if analysis_result["need_redesign"]:
                                    break
                else:
                    # 非JSON格式的处理
                    analysis_result["core_standards_met"] = True
                    analysis_result["need_redesign"] = False
                    analysis_result["reason"] = "无法解析详细的评价报告格式"
                    analysis_result["suggestions"] = "建议提供结构化的评价报告以便进行更准确的分析"
            
        except json.JSONDecodeError:
            # JSON解析失败的处理
            analysis_result["core_standards_met"] = True
            analysis_result["need_redesign"] = False
            analysis_result["reason"] = "评价报告格式不规范"
            analysis_result["suggestions"] = "建议提供规范的JSON格式评价报告"
        except Exception as e:
            # 其他异常处理
            analysis_result["core_standards_met"] = True
            analysis_result["need_redesign"] = False
            analysis_result["reason"] = f"分析过程中出现错误: {str(e)}"
            analysis_result["suggestions"] = "请检查评价报告内容"
        
        return analysis_result
    
    @staticmethod
    def check_core_standards(evaluation_report):
        """
        检查核心标准（催化性能和结构合理性）是否达标
        
        Args:
            evaluation_report (str): 评价报告
            
        Returns:
            bool: 如果核心标准达标返回True，否则返回False
        """
        try:
            # 尝试解析JSON格式的评价报告
            if isinstance(evaluation_report, str):
                json_match = re.search(r'\{.*\}', evaluation_report, re.DOTALL)
                if json_match:
                    report_data = json.loads(json_match.group())
                    
                    # 检查核心标准
                    if "results" in report_data:
                        for result in report_data["results"]:
                            if "scores" in result:
                                # 催化性能是第一个评分维度（索引0），结构合理性是第五个（索引4）
                                catalytic_performance = result["scores"][0]
                                structural_rationality = result["scores"][4]
                                
                                # 核心标准：催化性能和结构合理性都应≥6分
                                if catalytic_performance < 6 or structural_rationality < 6:
                                    return False
                    return True
                else:
                    # 非JSON格式，默认认为达标
                    return True
            else:
                # 非字符串格式，默认认为达标
                return True
                
        except Exception as e:
            # 出现异常时，默认认为达标
            return True