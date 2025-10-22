"""
Testes unitários para o framework de avaliação LLM.

Valida funcionamento do LLMEvaluator e componentes relacionados.
"""
import pytest
import json

from tests.utils.llm_evaluator import LLMEvaluator, EvaluationResult
from tests.utils.evaluation_criteria import RagEvaluationCriteria


class TestLLMEvaluator:
    """Testes core do avaliador."""
    
    def test_initialization_defaults(self):
        """Testa inicialização com valores padrão."""
        evaluator = LLMEvaluator()
        
        assert evaluator.threshold == 70
        assert evaluator.model == "gpt-5-nano"
        assert evaluator.llm is not None
    
    def test_initialization_custom(self):
        """Testa inicialização com valores customizados."""
        evaluator = LLMEvaluator(threshold=80, model="gpt-4")
        
        assert evaluator.threshold == 80
        assert evaluator.model == "gpt-4"
    
    def test_build_prompt_basic(self):
        """Testa construção de prompt sem SYSTEM_PROMPT."""
        evaluator = LLMEvaluator()
        
        prompt = evaluator.build_evaluation_prompt(
            question="Teste?",
            context="Contexto teste",
            response="Resposta teste"
        )
        
        assert "CONTEXTO FORNECIDO AO ASSISTENTE:" in prompt
        assert "Contexto teste" in prompt
        assert "PERGUNTA DO USUÁRIO:" in prompt
        assert "Teste?" in prompt
        assert "RESPOSTA DO ASSISTENTE:" in prompt
        assert "Resposta teste" in prompt
        assert "SYSTEM_PROMPT DO ASSISTENTE:" not in prompt
    
    def test_build_prompt_with_system_prompt(self):
        """Testa construção de prompt com SYSTEM_PROMPT."""
        evaluator = LLMEvaluator()
        
        system_prompt = "Você é um assistente."
        prompt = evaluator.build_evaluation_prompt(
            question="Teste?",
            context="Contexto teste",
            response="Resposta teste",
            system_prompt=system_prompt
        )
        
        assert "SYSTEM_PROMPT DO ASSISTENTE:" in prompt
        assert system_prompt in prompt


class TestEvaluationParsing:
    """Testes de parsing e construção de resultados."""
    
    def test_parse_valid_json(self):
        """Testa parsing de JSON válido."""
        evaluator = LLMEvaluator()
        
        json_text = json.dumps({
            "adherence_to_context": 80,
            "hallucination_detection": 90,
            "rule_following": 85,
            "clarity_objectivity": 75,
            "overall_score": 83,
            "feedback": "Boa resposta",
            "passed": True
        })
        
        result = evaluator._parse_evaluation_response(json_text)
        
        assert result["adherence_to_context"] == 80
        assert result["overall_score"] == 83
        assert result["passed"] is True
    
    def test_parse_json_with_markdown_blocks(self):
        """Testa parsing de JSON dentro de markdown code block."""
        evaluator = LLMEvaluator()
        
        json_text = """```json
{
    "adherence_to_context": 80,
    "hallucination_detection": 90,
    "rule_following": 85,
    "clarity_objectivity": 75,
    "overall_score": 83,
    "feedback": "Boa resposta",
    "passed": true
}
```"""
        
        result = evaluator._parse_evaluation_response(json_text)
        
        assert result["adherence_to_context"] == 80
        assert result["overall_score"] == 83
    
    def test_parse_invalid_json_raises(self):
        """Testa que JSON inválido levanta exceção."""
        evaluator = LLMEvaluator()
        
        invalid_json = "{ isso não é json válido"
        
        with pytest.raises(json.JSONDecodeError):
            evaluator._parse_evaluation_response(invalid_json)
    
    def test_build_result_complete(self):
        """Testa construção com todos os campos fornecidos."""
        evaluator = LLMEvaluator(threshold=70)
        
        data = {
            "adherence_to_context": 80,
            "hallucination_detection": 90,
            "rule_following": 85,
            "clarity_objectivity": 75,
            "overall_score": 83,
            "feedback": "Boa resposta",
            "passed": True
        }
        
        result = evaluator._build_evaluation_result(data)
        
        assert isinstance(result, EvaluationResult)
        assert result.score == 83
        assert result.overall_score == 83  # Alias
        assert result.passed is True
        assert result.feedback == "Boa resposta"
        assert result.criteria_scores["adherence_to_context"] == 80
    
    def test_build_result_calculates_missing_fields(self):
        """Testa que score e passed são calculados se não fornecidos."""
        evaluator = LLMEvaluator(threshold=70)
        
        # Teste com score faltando
        data = {
            "adherence_to_context": 80,
            "hallucination_detection": 90,
            "rule_following": 85,
            "clarity_objectivity": 75,
            "feedback": "Boa resposta"
        }
        
        result = evaluator._build_evaluation_result(data)
        
        # Score deve ser calculado com pesos
        expected_score = RagEvaluationCriteria.calculate_weighted_score({
            "adherence_to_context": 80,
            "hallucination_detection": 90,
            "rule_following": 85,
            "clarity_objectivity": 75,
        })
        
        assert result.score == expected_score
        assert result.passed is True  # Score acima de 70


class TestWeightedScore:
    """Testes de cálculo de score ponderado."""
    
    def test_calculate_weighted_score_normal(self):
        """Testa cálculo de score ponderado com pesos corretos."""
        scores = {
            "adherence_to_context": 80,      # 30% = 24
            "hallucination_detection": 90,   # 30% = 27
            "rule_following": 85,            # 25% = 21.25
            "clarity_objectivity": 75,       # 15% = 11.25
        }
        # Total = 24 + 27 + 21.25 + 11.25 = 83.5 -> 84 (arredondado)
        
        result = RagEvaluationCriteria.calculate_weighted_score(scores)
        
        assert result == 84
    
    def test_calculate_weighted_score_edge_cases(self):
        """Testa cálculo com edge cases (zeros e cem)."""
        # Teste com todos zeros
        scores_zero = {
            "adherence_to_context": 0,
            "hallucination_detection": 0,
            "rule_following": 0,
            "clarity_objectivity": 0,
        }
        
        result_zero = RagEvaluationCriteria.calculate_weighted_score(scores_zero)
        assert result_zero == 0
        
        # Teste com todos cem
        scores_hundred = {
            "adherence_to_context": 100,
            "hallucination_detection": 100,
            "rule_following": 100,
            "clarity_objectivity": 100,
        }
        
        result_hundred = RagEvaluationCriteria.calculate_weighted_score(scores_hundred)
        assert result_hundred == 100


class TestEvaluationCriteria:
    """Testes dos critérios de avaliação."""
    
    def test_all_criteria_structure(self):
        """Testa estrutura de todos os critérios."""
        criteria = RagEvaluationCriteria.get_all_criteria()
        
        assert len(criteria) == 4
        assert all(hasattr(c, 'name') for c in criteria)
        assert all(hasattr(c, 'weight') for c in criteria)
        assert all(hasattr(c, 'description') for c in criteria)
    
    def test_weights_sum_to_one(self):
        """Testa que pesos dos critérios somam 1.0."""
        criteria = RagEvaluationCriteria.get_all_criteria()
        
        total_weight = sum(c.weight for c in criteria)
        
        assert abs(total_weight - 1.0) < 0.01  # Tolerância para float

