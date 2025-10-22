#!/usr/bin/env python
"""
Analisa relatório de cobertura e identifica gaps.
"""
import json
import sys
from pathlib import Path


def load_coverage_report():
    """Carrega relatório de cobertura."""
    coverage_file = Path(".coverage")
    
    if not coverage_file.exists():
        print("❌ Arquivo .coverage não encontrado")
        print("   Execute: pytest --cov=src")
        sys.exit(1)
    
    # Importar coverage para análise
    from coverage import Coverage
    
    cov = Coverage()
    cov.load()
    
    return cov


def analyze_module_coverage(cov, module_path):
    """Analisa cobertura de um módulo específico."""
    try:
        analysis = cov.analysis(module_path)
    except Exception as e:
        # Módulo não encontrado ou não analisado
        return None
    
    # analysis = (filename, executed, excluded, missing)
    filename, executed, excluded, missing = analysis
    
    total_lines = len(executed) + len(missing)
    coverage_pct = (len(executed) / total_lines * 100) if total_lines > 0 else 0
    
    return {
        "filename": filename,
        "total_lines": total_lines,
        "executed": len(executed),
        "missing": len(missing),
        "coverage": coverage_pct,
        "missing_lines": sorted(missing),
    }


def main():
    """Análise principal."""
    print("📊 Análise de Cobertura\n")
    
    cov = load_coverage_report()
    
    # Módulos a analisar
    modules = [
        "src/ingest.py",
        "src/search.py",
        "src/chat.py",
    ]
    
    results = []
    
    for module in modules:
        result = analyze_module_coverage(cov, module)
        if result:
            results.append(result)
        else:
            print(f"⚠️  Módulo {module} não encontrado ou não analisado")
    
    if not results:
        print("❌ Nenhum módulo foi analisado")
        return 1
    
    # Exibir resultados
    print("=" * 70)
    print(f"{'Módulo':<30} {'Cobertura':<15} {'Linhas':<15}")
    print("=" * 70)
    
    total_coverage = 0
    
    for result in results:
        module_name = result['filename'].split('/')[-1]
        coverage = result['coverage']
        lines = f"{result['executed']}/{result['total_lines']}"
        
        # Cor baseada em cobertura
        if coverage >= 80:
            status = "✅"
        elif coverage >= 60:
            status = "⚠️ "
        else:
            status = "❌"
        
        print(f"{status} {module_name:<27} {coverage:>6.1f}%       {lines:<15}")
        
        # Linhas não cobertas
        if result['missing_lines']:
            print(f"   Linhas não cobertas: {result['missing_lines'][:10]}")
            if len(result['missing_lines']) > 10:
                print(f"   ... e mais {len(result['missing_lines']) - 10} linhas")
        
        total_coverage += coverage
    
    print("=" * 70)
    
    avg_coverage = total_coverage / len(results) if results else 0
    
    print(f"\n📈 Cobertura Média: {avg_coverage:.1f}%")
    
    if avg_coverage >= 80:
        print("✅ Cobertura adequada (>= 80%)")
        return 0
    else:
        print("❌ Cobertura insuficiente (< 80%)")
        print("\n🎯 Ações recomendadas:")
        print("   1. Adicionar testes para linhas não cobertas")
        print("   2. Revisar se linhas são realmente testáveis")
        print("   3. Considerar remover código não utilizado")
        return 1


if __name__ == "__main__":
    sys.exit(main())
