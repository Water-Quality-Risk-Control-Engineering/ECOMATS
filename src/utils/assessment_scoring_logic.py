#!/usr/bin/env python3
"""
Assessment Scoring Logic Module.
Provides unified scoring logic to ensure assessment agent evaluations are based on the model's own rational judgment.
"""

import logging
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class AssessmentScoringLogic:
    """Assessment Scoring Logic Class - Provides unified scoring logic."""
    
    # Dimension weights
    DIMENSION_WEIGHTS = {
        "catalytic": 0.50,      # Catalytic performance
        "economic": 0.10,       # Economic feasibility
        "environmental": 0.10,  # Environmental friendliness
        "technical": 0.10,      # Technical feasibility
        "structural": 0.20      # Structural rationality
    }
    
    # Scoring criteria
    SCORE_CRITERIA = {
        10: "Exceptional - Outstanding performance, fully validated",
        9: "Excellent - Strong scientific value, well-designed structure",
        8: "Very Good - Stable performance, minor improvements needed",
        7: "Good - Above average, some limitations",
        6: "Average - Acceptable performance, noticeable limitations",
        5: "Below Average - Moderate performance, major issues",
        4: "Poor - Low performance, major defects",
        3: "Very Poor - Minimal performance, critical defects",
        2: "Invalid - Serious issues, fundamental errors",
        1: "Completely Invalid - Chemically impossible or non-existent"
    }
    
    @staticmethod
    def calculate_weighted_score(scores: List[int]) -> float:
        """
        Calculate weighted total score.
        
        Args:
            scores (List[int]): Five dimension scores [catalytic performance, economic feasibility, environmental friendliness, technical feasibility, structural rationality]
            
        Returns:
            float: Weighted total score
        """
        if len(scores) != 5:
            raise ValueError("Scores must include five dimensions")
        
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
        Validate if chemical formula is chemically impossible.
        
        Args:
            formula (str): Material chemical formula
            
        Returns:
            bool: True if chemically impossible, False otherwise
        """
        # Check for obviously chemically impossible cases
        impossible_patterns = [
            "IrO7",      # Ir +14 impossible
            "Ru(SO4)9",  # Ru +18 impossible
            "FeO4",      # Fe +8 impossible
            "Hg(Cl)5"    # Hg +5 impossible
        ]
        
        return any(pattern in formula for pattern in impossible_patterns)
    
    @staticmethod
    def validate_ambiguous_formula(formula: str) -> bool:
        """
        Validate if chemical formula is ambiguous.
        
        Args:
            formula (str): Material chemical formula
            
        Returns:
            bool: True if formula is ambiguous, False otherwise
        """
        # Check for ambiguous chemical formula representations
        ambiguous_patterns = [
            "Pd/Au",     # No ratio specified
        ]
        
        return any(pattern in formula for pattern in ambiguous_patterns)
    
    @staticmethod
    def adjust_scores_based_on_tool_validation(scores: List[int], tool_validation_result: Dict[str, Any]) -> List[int]:
        """
        Adjust scores based on tool validation results.
        
        Args:
            scores (List[int]): Original scores
            tool_validation_result (Dict[str, Any]): Tool validation results
            
        Returns:
            List[int]: Adjusted scores
        """
        adjusted_scores = scores.copy()
        
        # If tool validation fails, reduce scores appropriately
        if not tool_validation_result.get("all_valid", True):
            # Reduce scores for all dimensions, but not below 1
            adjusted_scores = [max(1, score - 1) for score in scores]
            logger.warning(f"Tool validation failed, scores adjusted: {scores} -> {adjusted_scores}")
        
        return adjusted_scores
    
    @staticmethod
    def ensure_consistent_scoring(expert_a_scores: List[int], expert_b_scores: List[int], expert_c_scores: List[int]) -> Tuple[List[int], List[int], List[int]]:
        """
        Ensure consistency among three assessment agent scores.
        
        Args:
            expert_a_scores (List[int]): Expert A's scores
            expert_b_scores (List[int]): Expert B's scores
            expert_c_scores (List[int]): Expert C's scores
            
        Returns:
            Tuple[List[int], List[int], List[int]]: Adjusted scores
        """
        # Calculate average score for each dimension
        avg_scores = []
        for i in range(5):
            avg = (expert_a_scores[i] + expert_b_scores[i] + expert_c_scores[i]) / 3
            avg_scores.append(round(avg))
        
        # If an expert's score differs too much from average (more than 2 points), adjust it
        def adjust_score(score, avg):
            if abs(score - avg) > 2:
                # Adjust score to move closer to average by 1 point
                if score > avg:
                    return score - 1
                else:
                    return score + 1
            return score
        
        adjusted_a_scores = [adjust_score(expert_a_scores[i], avg_scores[i]) for i in range(5)]
        adjusted_b_scores = [adjust_score(expert_b_scores[i], avg_scores[i]) for i in range(5)]
        adjusted_c_scores = [adjust_score(expert_c_scores[i], avg_scores[i]) for i in range(5)]
        
        return adjusted_a_scores, adjusted_b_scores, adjusted_c_scores
