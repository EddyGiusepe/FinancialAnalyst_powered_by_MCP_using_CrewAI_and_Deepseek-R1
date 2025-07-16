#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script server.py
================
Este script implementa um servidor MCP (Model Context Protocol) para análise financeira.
"""
from mcp.server.fastmcp import FastMCP
from finance_crew import run_financial_analysis

# Cria uma instância FastMCP:
mcp = FastMCP("financial-analyst")

@mcp.tool()
def analyze_stock(query: str) -> str:
    """
    Analisa dados do mercado de ações com base na consulta e gera código Python executável para análise e visualização.
    Retorna um script Python formatado pronto para execução.
    
    A consulta é uma string que deve conter o símbolo da ação (exemplo: TSLA, AAPL, NVDA, etc.), 
    período de tempo (exemplo: 1 dia, 1 mês, 1 ano), e a ação a ser realizada (exemplo: plotar, analisar, comparar).

    Exemplos de consultas:
    - "Mostre-me o desempenho da ação da Tesla nos últimos 3 meses"
    - "Compare as ações da Apple e da Microsoft nos últimos 12 meses"
    - "Analise o volume de negociação da ação da Amazon nos últimos 30 dias"

    Args:
        query (str): A consulta para analisar os dados do mercado de ações.
    
    Returns:
        str: Um código Python formatado pronto para execução.
    """
    try:
        result = run_financial_analysis(query)
        return result
    except Exception as e:
        return f"Erro: {e}"
    

@mcp.tool()
def save_code(code: str) -> str:
    """
    Espera um código Python formatado, pronto para execução e executável como entrada em forma de string. 
    Salva o código fornecido em um arquivo stock_analysis.py, certifique-se de que o código é um arquivo 
    Python válido, formatado e pronto para execução.

    Args:
        code (str): O código Python formatado, pronto para execução e executável como string.
    
    Returns:
        str: Uma mensagem indicando que o código foi salvo com sucesso.
    """
    try:
        with open('stock_analysis.py', 'w') as f:
            f.write(code)
        return "Código salvo em stock_analysis.py"
    except Exception as e:
        return f"Erro: {e}"

@mcp.tool()
def run_code_and_show_plot() -> str:
    """
    Executa o código em stock_analysis.py e gera o gráfico
    """
    with open('stock_analysis.py', 'r') as f:
        exec(f.read())

# Executa o servidor (server) localmente:
if __name__ == "__main__":
    mcp.run(transport='stdio')
    