#!/usr/bin/env python3
"""
评估评分逻辑模块
提供统一的评分逻辑，确保评估代理的主体评判基于模型自身理性判断
"""

import logging
from typing import Dict, Any, List, Tuple

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScoringLogic:
    """评估评分逻辑类 - 提供统一的评分逻辑"""
    
    # 评分维度权重
    DIMENSION_WEIGHTS = {
        "catalytic": 0.50,      # 催化性能
        "economic": 0.10,       # 经济可行性
        "environmental": 0.10,  # 环境友好性
        "technical": 0.10,      # 技术可行性
        "structural": 0.20      # 结构合理性
    }
    
    # 评分标准
    SCORE_CRITERIA = {
        10: "Exceptional - 突出性能，全面验证",
        9: "Excellent - 强科学价值，结构设计良好",
        8: "Very Good - 性能稳定，需要少量改进",
        7: "Good - 高于平均水平，有一些限制",
        6: "Average - 可接受的性能，有明显限制",
        5: "Below Average - 中等性能，有重大问题",
        4: "Poor - 低性能，有主要缺陷",
        3: "Very Poor - 最低性能，有关键性缺陷",
        2: "Invalid - 严重问题，根本性错误",
        1: "Completely Invalid - 化学上不可能或不存在"
    }
    
    @staticmethod
    def calculate_weighted_score(scores: List[int]) -> float:
        """
        计算加权总分
        
        Args:
            scores (List[int]): 五个维度的评分 [催化性能, 经济可行性, 环境友好性, 技术可行性, 结构合理性]
            
        Returns:
            float: 加权总分
        """
        if len(scores) != 5:
            raise ValueError("评分必须包含五个维度")
        
        weighted_total = (
            scores[0] * AssessmentScoringLogic.DIMENSION_WEIGHTS["catalytic"] +
            scores[1] * AssessmentScoringLogic.DIMENSION_WEIGHTS["economic"] +
            scores[2] * AssessmentScoringLogic.DIMENSION_WEIGHTS["environmental"] +
            scores[3] * AssessmentScoringLogic.DIMENSION_WEIGHTS["technical"] +
            scores[4] * AssessmentScoringLogic.DIMENSION_WEIGHTS["structural"]
        )
        
        return round(weighted_total, 2)
    
    @staticmethod
    def validate_chemically_impossible(formula: str) -> bool:
        """
        验证化学式是否化学上不可能
        
        Args:
            formula (str): 材料化学式
            
        Returns:
            bool: 如果化学上不可能返回True，否则返回False
        """
        # 检查一些明显的化学上不可能的情况
        impossible_patterns = [
            "IrO7",      # Ir +14 不可能
            "Ru(SO4)9",  # Ru +18 不可能
            "FeO4",      # Fe +8 不可能
            "Hg(Cl)5"    # Hg +5 不可能
        ]
        
        return any(pattern in formula for pattern in impossible_patterns)
    
    @staticmethod
    def validate_ambiguous_formula(formula: str) -> bool:
        """
        验证化学式是否不明确
        
        Args:
            formula (str): 材料化学式
            
        Returns:
            bool: 如果化学式不明确返回True，否则返回False
        """
        # 检查不明确的化学式表示
        ambiguous_patterns = [
            "Pd/Au",     # 没有比例
        ]
        
        return any(pattern in formula for pattern in ambiguous_patterns)
    
    @staticmethod
    def adjust_scores_based_on_tool_validation(scores: List[int], tool_validation_result: Dict[str, Any]) -> List[int]:
        """
        根据工具验证结果调整评分
        
        Args:
            scores (List[int]): 原始评分
            tool_validation_result (Dict[str, Any]): 工具验证结果
            
        Returns:
            List[int]: 调整后的评分
        """
        adjusted_scores = scores.copy()
        
        # 如果工具验证失败，适当降低评分
        if not tool_validation_result.get("all_valid", True):
            # 降低所有维度的评分，但不低于1
            adjusted_scores = [max(1, score - 1) for score in scores]
            logger.warning(f"工具验证失败，评分已调整: {scores} -> {adjusted_scores}")
        
        return adjusted_scores
    
    @staticmethod
    def ensure_consistent_scoring(expert_a_scores: List[int], expert_b_scores: List[int], expert_c_scores: List[int]) -> Tuple[List[int], List[int], List[int]]:
        """
        确保三个评估代理的评分一致性
        
        Args:
            expert_a_scores (List[int]): 专家A的评分
            expert_b_scores (List[int]): 专家B的评分
            expert_c_scores (List[int]): 专家C的评分
            
        Returns:
            Tuple[List[int], List[int], List[int]]: 调整后的评分
        """
        # 计算每个维度的平均分
        avg_scores = []
        for i in range(5):
            avg = (expert_a_scores[i] + expert_b_scores[i] + expert_c_scores[i]) / 3
            avg_scores.append(round(avg))
        
        # 如果某个专家的评分与平均分相差太大（超过2分），则进行调整
        def adjust_score(score, avg):
            if abs(score - avg) > 2:
                # 调整评分为向平均分靠近1分
                if score > avg:
                    return score - 1
                else:
                    return score + 1
            return score
        
        adjusted_a_scores = [adjust_score(expert_a_scores[i], avg_scores[i]) for i in range(5)]
        adjusted_b_scores = [adjust_score(expert_b_scores[i], avg_scores[i]) for i in range(5)]
        adjusted_c_scores = [adjust_score(expert_c_scores[i], avg_scores[i]) for i in range(5)]
        
        return adjusted_a_scores, adjusted_b_scores, adjusted_c_scores