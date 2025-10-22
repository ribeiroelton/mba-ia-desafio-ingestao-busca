"""
Critérios de avaliação estruturados para respostas LLM.

Define critérios reutilizáveis específicos para sistemas RAG.
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EvaluationCriterion:
    """Critério de avaliação para respostas LLM."""
    name: str
    weight: float  # 0.0-1.0
    description: str


class RagEvaluationCriteria:
    """Critérios de avaliação específicos para sistemas RAG."""
    
    ADHERENCE_TO_CONTEXT = EvaluationCriterion(
        name="adherence_to_context",
        weight=0.30,
        description="Resposta baseada exclusivamente no contexto fornecido"
    )
    
    HALLUCINATION_DETECTION = EvaluationCriterion(
        name="hallucination_detection",
        weight=0.30,
        description="Detecção de alucinações e informações inventadas"
    )
    
    RULE_FOLLOWING = EvaluationCriterion(
        name="rule_following",
        weight=0.25,
        description="Seguimento rigoroso do SYSTEM_PROMPT"
    )
    
    CLARITY_OBJECTIVITY = EvaluationCriterion(
        name="clarity_objectivity",
        weight=0.15,
        description="Clareza e objetividade da resposta"
    )
    
    @classmethod
    def get_all_criteria(cls) -> List[EvaluationCriterion]:
        """Retorna todos os critérios de avaliação."""
        return [
            cls.ADHERENCE_TO_CONTEXT,
            cls.HALLUCINATION_DETECTION,
            cls.RULE_FOLLOWING,
            cls.CLARITY_OBJECTIVITY,
        ]
    
    @classmethod
    def calculate_weighted_score(cls, scores: Dict[str, int]) -> int:
        """
        Calcula score ponderado baseado nos critérios.
        
        Args:
            scores: Dict com scores por critério (0-100)
            
        Returns:
            Score total ponderado (0-100)
            
        Example:
            >>> scores = {
            ...     "adherence_to_context": 80,
            ...     "hallucination_detection": 90,
            ...     "rule_following": 85,
            ...     "clarity_objectivity": 75,
            ... }
            >>> RagEvaluationCriteria.calculate_weighted_score(scores)
            83
        """
        criteria = cls.get_all_criteria()
        total_score = 0.0
        
        for criterion in criteria:
            score = scores.get(criterion.name, 0)
            total_score += score * criterion.weight
        
        return int(round(total_score))
