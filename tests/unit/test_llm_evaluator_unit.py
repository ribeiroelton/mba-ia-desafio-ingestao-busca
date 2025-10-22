"""
Testes unitários para o framework de avaliação LLM.

Valida funcionamento do LLMEvaluator e componentes relacionados.
"""
import pytest
import json

from tests.utils.llm_evaluator import LLMEvaluator, EvaluationResult
from tests.utils.evaluation_criteria import RagEvaluationCriteria


class TestLLMEvaluatorInitialization:
    """Testes de inicialização do avaliador."""
    
    def test_default_initialization(self):
        """Testa inicialização com valores padrão."""
        evaluator = LLMEvaluator()
        
        assert evaluator.threshold == 70
        assert evaluator.model == "gpt-5-nano"
        assert evaluator.llm is not None
    
    def test_custom_initialization(self):
        """Testa inicialização com valores customizados."""
        evaluator = LLMEvaluator(threshold=80, model="gpt-4")
        
        assert evaluator.threshold == 80
        assert evaluator.model == "gpt-4"


class TestPromptBuilding:
    """Testes de construção de prompts."""
    
    def test_build_prompt_without_system_prompt(self):
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


class TestJSONParsing:
    """Testes de parsing de JSON."""
    
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
    
    def test_parse_json_with_markdown(self):
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
    
    def test_parse_invalid_json_raises_error(self):
        """Testa que JSON inválido levanta exceção."""
        evaluator = LLMEvaluator()
        
        invalid_json = "{ isso não é json válido"
        
        with pytest.raises(json.JSONDecodeError):
            evaluator._parse_evaluation_response(invalid_json)


class TestEvaluationResultBuilding:
    """Testes de construção de EvaluationResult."""
    
    def test_build_result_with_all_fields(self):
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
    
    def test_build_result_calculates_score_if_missing(self):
        """Testa que score é calculado se não fornecido."""
        evaluator = LLMEvaluator(threshold=70)
        
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
    
    def test_build_result_determines_passed_if_missing(self):
        """Testa que passed é determinado pelo threshold se não fornecido."""
        evaluator = LLMEvaluator(threshold=70)
        
        # Score acima do threshold
        data_pass = {
            "adherence_to_context": 80,
            "hallucination_detection": 90,
            "rule_following": 85,
            "clarity_objectivity": 75,
            "overall_score": 83,
            "feedback": "Boa resposta"
        }
        
        result_pass = evaluator._build_evaluation_result(data_pass)
        assert result_pass.passed is True
        
        # Score abaixo do threshold
        data_fail = {
            "adherence_to_context": 50,
            "hallucination_detection": 60,
            "rule_following": 55,
            "clarity_objectivity": 45,
            "overall_score": 54,
            "feedback": "Resposta fraca"
        }
        
        result_fail = evaluator._build_evaluation_result(data_fail)
        assert result_fail.passed is False


class TestWeightedScoreCalculation:
    """Testes de cálculo de score ponderado."""
    
    def test_calculate_weighted_score(self):
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
    
    def test_calculate_weighted_score_all_zeros(self):
        """Testa cálculo com todos os scores zero."""
        scores = {
            "adherence_to_context": 0,
            "hallucination_detection": 0,
            "rule_following": 0,
            "clarity_objectivity": 0,
        }
        
        result = RagEvaluationCriteria.calculate_weighted_score(scores)
        
        assert result == 0
    
    def test_calculate_weighted_score_all_hundreds(self):
        """Testa cálculo com todos os scores 100."""
        scores = {
            "adherence_to_context": 100,
            "hallucination_detection": 100,
            "rule_following": 100,
            "clarity_objectivity": 100,
        }
        
        result = RagEvaluationCriteria.calculate_weighted_score(scores)
        
        assert result == 100


class TestEvaluationCriteria:
    """Testes dos critérios de avaliação."""
    
    def test_get_all_criteria(self):
        """Testa obtenção de todos os critérios."""
        criteria = RagEvaluationCriteria.get_all_criteria()
        
        assert len(criteria) == 4
        assert all(hasattr(c, 'name') for c in criteria)
        assert all(hasattr(c, 'weight') for c in criteria)
        assert all(hasattr(c, 'description') for c in criteria)
    
    def test_criteria_weights_sum_to_one(self):
        """Testa que pesos dos critérios somam 1.0."""
        criteria = RagEvaluationCriteria.get_all_criteria()
        
        total_weight = sum(c.weight for c in criteria)
        
        assert abs(total_weight - 1.0) < 0.01  # Tolerância para float
    
    def test_criteria_have_examples(self):
        """Testa que todos os critérios têm exemplos."""
        criteria = RagEvaluationCriteria.get_all_criteria()
        
        for criterion in criteria:
            assert len(criterion.examples_good) > 0
            assert len(criterion.examples_bad) > 0
