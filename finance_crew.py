#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script finance_crew.py
======================
Este script implementa um fluxo de trabalho de análise financeira 
que analisa dados do mercado de ações e fornece insights.
"""
import re
import json
import os
import yfinance as yf
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import CodeInterpreterTool, FileReadTool
from config.settings import OPENAI_API_KEY

class QueryAnalysisOutput(BaseModel):
    """Saída estruturada para a tarefa de análise de consulta."""
    symbol: str = Field(description="Símbolo de cotação de ações. Exemplo: TSLA, AAPL.")
    timeframe: str = Field(description="Período de tempo. Exemplo: '1 dia', '1 mês', '1 ano'.")
    action: str = Field(description="Ação a ser realizada. Exemplo: 'buscar', 'plotar'.")

llm = LLM(
    model="ollama/deepseek-r1:7b",
    base_url="http://localhost:11434",
    # temperature=0.7
)

#llm = LLM(
#     model="openai/gpt-4o",
#     api_key=OPENAI_API_KEY,
#     # temperature=0.7
#)

# 1) Agente de análise de consulta:
query_parser_agent = Agent(
    role="Analista de Dados de Ações",
    goal="Extrair detalhes das ações e buscar dados necessários a partir da consulta do usuário: {query}.",
    backstory="Você é um analista financeiro especializado em recuperação de dados de mercado de ações.",
    llm=llm,
    verbose=True,
    memory=True,
)

query_parsing_task = Task(
    description="Analise a consulta do usuário e extraia detalhes das ações.",
    expected_output="Um dicionário com as chaves: 'symbol', 'timeframe', 'action'.",
    output_pydantic=QueryAnalysisOutput,
    agent=query_parser_agent,
)


# 2) Agente de escrita de código:
code_writer_agent = Agent(
    role="Desenvolvedor Python Senior",
    goal="Escrever código Python para visualizar dados de ações.",
    backstory="""Você é um desenvolvedor Python Senior especializado em visualização de dados de mercado de ações. 
                 Você também é um especialista em bibliotecas Pandas, Matplotlib e yfinance.
                 Você é habilidoso em escrever código Python pronto para produção.""",
    llm=llm,
    verbose=True,
)

code_writer_task = Task(
    description="""Escreva código Python para visualizar dados de ações com base nas entradas do analista de ações,
                   onde você encontrará o símbolo da ação, o período de tempo e a ação.""",
    expected_output="Um arquivo Python (.py) limpo e executável para visualização de ações.",
    agent=code_writer_agent,
)


# 3) Agente interpretador de código (usa a ferramenta de interpretação de código da Crewai):
code_interpreter_tool = CodeInterpreterTool()

code_execution_agent = Agent(
    role="Especialista Sênior em Execução de Código",
    goal="Revise e execute o código Python gerado pelo agente de escrita de código para visualizar dados de estoque.",
    backstory="Você é um especialista em execução de código. Você é habilidoso em executar código Python.",
    # tools=[code_interpreter_tool],
    allow_code_execution=True,   # Esta linha automaticamente adiciona o CodeInterpreterTool
    llm=llm,
    verbose=True,
)

code_execution_task = Task(
    description="""Revise e execute o código Python gerado pelo agente de escrita de código para visualizar dados de estoque.""",
    expected_output="Um arquivo de script Python limpo e executável (.py) para visualização de ações.",
    agent=code_execution_agent,
)

# Criar a crew:
crew = Crew(
    agents=[query_parser_agent, code_writer_agent, code_execution_agent],
    tasks=[query_parsing_task, code_writer_task, code_execution_task],
    process=Process.sequential
)

# Função para ser um wrapped dentro da tool MCP:
def run_financial_analysis(query):
    result = crew.kickoff(inputs={"query": query})
    return result.raw

if __name__ == "__main__":
    # Executar a crew com uma consulta
    # query = input("Insira a ação (stock) para analisar: ")
    result = crew.kickoff(inputs={"query": "Plote a ação YTD de Tesla"})
    print(result.raw)
    