#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

client_finance.py
================
Cliente MCP para interagir com o servidor de análise financeira (server.py).
Este cliente permite fazer consultas sobre ações e receber análises financeiras.

Run
===
uv run client_finance.py /home/eddygiusepe/1_github/FinancialAnalyst_powered_by_MCP_using_CrewAI_and_Deepseek-R1/server.py
"""
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
import sys
import os

# Adiciona o diretório raiz do projeto ao PATH do Python:
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import ANTHROPIC_API_KEY


class FinanceClient:
    def __init__(self):
        # Inicia session e client objects:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

    async def connect_to_server(self, server_script_path: str):
        """Conecta ao servidor MCP de análise financeira

        Args:
            server_script_path: Caminho para o script do servidor (.py)
        """
        if not server_script_path.endswith(".py"):
            raise ValueError("O script do servidor deve ser um arquivo Python (.py)")

        server_params = StdioServerParameters(
            command="python", args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # Lista ferramentas disponíveis:
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConectado ao servidor com ferramentas:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Processa uma consulta financeira usando Claude e as ferramentas do servidor"""
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]

        # Chamada API Claude inicial:
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=messages,
            tools=available_tools,
            temperature=0.1
        )

        # Processa resposta e lida com chamadas de ferramenta:
        final_text = []
        saved_code = False
        executed_plot = False

        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Executa chamada de ferramenta:
                result = await self.session.call_tool(tool_name, tool_args)
                
                # Se for analyze_stock, podemos salvar o código resultante
                if tool_name == "analyze_stock":
                    final_text.append(f"\n[Analisando ação: {tool_args['query']}]")
                    code = result.content
                    # Salva o código automaticamente se a análise foi bem-sucedida
                    if not code.startswith("Erro:"):
                        save_result = await self.session.call_tool("save_code", {"code": code})
                        saved_code = True
                        final_text.append("\n[Código da análise salvo com sucesso]")
                
                # Se for save_code, registra que salvamos o código
                elif tool_name == "save_code":
                    saved_code = True
                    final_text.append(f"\n[{result.content}]")
                
                # Se for run_code_and_show_plot, executa o plot se o código já foi salvo
                elif tool_name == "run_code_and_show_plot":
                    if saved_code:
                        await self.session.call_tool("run_code_and_show_plot", {})
                        executed_plot = True
                        final_text.append("\n[Gráfico gerado e exibido]")
                    else:
                        final_text.append("\n[Erro: Nenhum código foi salvo para executar]")
                
                # Continue a conversa com os resultados da ferramenta:
                if hasattr(content, "text") and content.text:
                    messages.append({"role": "assistant", "content": content.text})
                messages.append({"role": "user", "content": result.content})

                # Obtém próxima resposta do Claude:
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        # Se analisamos e salvamos o código, mas não executamos o plot, faça isso agora
        if saved_code and not executed_plot:
            try:
                await self.session.call_tool("run_code_and_show_plot", {})
                final_text.append("\n[Gráfico gerado e exibido automaticamente]")
            except Exception as e:
                final_text.append(f"\n[Erro ao gerar o gráfico: {str(e)}]")

        return "\n".join(final_text)

    async def chat_loop(self):
        """Executa um loop de chat interativo para análise financeira"""
        print("\n🤖 Analista Financeiro MCP Iniciado 📈")
        print("Digite suas consultas sobre ações ou 'sair' para encerrar.")
        print("\nExemplos de consultas:")
        print("- 'Mostre-me o desempenho da ação da Tesla nos últimos 3 meses'")
        print("- 'Compare as ações da Apple e da Microsoft no último ano'")
        print("- 'Analise o volume de negociação da NVDA nos últimos 30 dias'")

        while True:
            try:
                query = input("\nDigite sua consulta: ").strip()

                if query.lower() in ["sair", "quit", "exit"]:
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nErro: {str(e)}")

    async def cleanup(self):
        """Limpa recursos"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Uso: python client_finance.py <caminho_para_server.py>")
        sys.exit(1)

    client = FinanceClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())