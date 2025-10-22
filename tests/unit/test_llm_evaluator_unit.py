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


class TestCriteriaExamplesUsage:
    """Testes para validar uso dos exemplos de critérios."""
    
    def test_get_criteria_examples_text(self):
        """Testa formatação de exemplos de um critério."""
        text = RagEvaluationCriteria.get_criteria_examples_text("adherence_to_context")
        
        # Validar estrutura
        assert "CRITÉRIO: ADHERENCE_TO_CONTEXT" in text
        assert "Peso:" in text
        assert "Descrição:" in text
        assert "✓ EXEMPLOS DE RESPOSTAS BOM:" in text
        assert "✗ EXEMPLOS DE RESPOSTAS RUIM:" in text
        
        # Validar conteúdo dos exemplos
        assert "cita trecho exato do contexto" in text
        assert "inclui fatos não presentes no contexto" in text
    
    def test_get_criteria_examples_text_all_criteria(self):
        """Testa formatação de exemplos para todos os critérios."""
        criteria = RagEvaluationCriteria.get_all_criteria()
        
        for criterion in criteria:
            text = RagEvaluationCriteria.get_criteria_examples_text(criterion.name)
            
            # Validar que cada exemplo está presente no texto formatado
            for good_example in criterion.examples_good:
                assert good_example in text, f"Exemplo bom não encontrado: {good_example}"
            
            for bad_example in criterion.examples_bad:
                assert bad_example in text, f"Exemplo ruim não encontrado: {bad_example}"
    
    def test_get_criteria_examples_text_invalid_criterion(self):
        """Testa erro ao tentar formatar exemplo de critério inexistente."""
        with pytest.raises(ValueError, match="Critério 'invalid_criterion' não encontrado"):
            RagEvaluationCriteria.get_criteria_examples_text("invalid_criterion")
    
    def test_evaluator_system_prompt_includes_examples(self):
        """Testa que EVALUATOR_SYSTEM_PROMPT inclui exemplos de critérios."""
        prompt = LLMEvaluator.EVALUATOR_SYSTEM_PROMPT
        
        # Validar que exemplos estão no prompt
        assert "✓ EXEMPLOS DE BOAS RESPOSTAS:" in prompt
        assert "✗ EXEMPLOS DE MÁS RESPOSTAS:" in prompt
        
        # Validar que alguns exemplos específicos estão presentes
        assert "cita trecho exato do contexto" in prompt
        assert "inventa estatísticas não presentes" in prompt
        assert "Não produz opiniões ou interpretações" in prompt
    
    def test_get_failing_criterion_guidance_no_failures(self):
        """Testa guia de critérios quando nenhum falhou."""
        result = EvaluationResult(
            score=85,
            criteria_scores={
                "adherence_to_context": 85,
                "hallucination_detection": 90,
                "rule_following": 80,
                "clarity_objectivity": 75,
            },
            feedback="Tudo bem",
            passed=True,
            details={}
        )
        
        guidance = LLMEvaluator.get_failing_criterion_guidance(result)
        
        assert "✓ Nenhum critério falhou!" in guidance
    
    def test_get_failing_criterion_guidance_with_failures(self):
        """Testa guia de critérios quando há falhas."""
        result = EvaluationResult(
            score=55,
            criteria_scores={
                "adherence_to_context": 40,
                "hallucination_detection": 30,
                "rule_following": 75,
                "clarity_objectivity": 80,
            },
            feedback="Detectadas alucinações e fatos externos",
            passed=False,
            details={}
        )
        
        guidance = LLMEvaluator.get_failing_criterion_guidance(result, threshold=70)
        
        # Validar estrutura
        assert "⚠️ CRITÉRIOS COM FALHA" in guidance
        assert "HALLUCINATION_DETECTION" in guidance  # Nome formatado com underscore em caps
        assert "ADHERENCE_TO_CONTEXT" in guidance  # Nome formatado com underscore em caps
        assert "Detectadas alucinações e fatos externos" in guidance
        
        # Validar que exemplos dos critérios que falharam estão presentes
        assert "✓ EXEMPLOS DE RESPOSTAS BOM:" in guidance
        assert "✗ EXEMPLOS DE RESPOSTAS RUIM:" in guidance
    
    def test_get_failing_criterion_guidance_ordering(self):
        """Testa que critérios falhando aparecem ordenados por score (pior primeiro)."""
        result = EvaluationResult(
            score=50,
            criteria_scores={
                "adherence_to_context": 60,
                "hallucination_detection": 20,  # Pior
                "rule_following": 50,  # Intermediário
                "clarity_objectivity": 80,
            },
            feedback="Feedback teste",
            passed=False,
            details={}
        )
        
        guidance = LLMEvaluator.get_failing_criterion_guidance(result, threshold=70)
        
        # Verificar que hallucination_detection (score 20) aparece antes de rule_following (score 50)
        hallucination_pos = guidance.find("HALLUCINATION_DETECTION")
        rule_following_pos = guidance.find("RULE_FOLLOWING")
        
        assert hallucination_pos != -1, "HALLUCINATION_DETECTION não encontrado no guidance"
        assert rule_following_pos != -1, "RULE_FOLLOWING não encontrado no guidance"
        assert hallucination_pos < rule_following_pos, \
            "Critério com score mais baixo deveria aparecer primeiro"
