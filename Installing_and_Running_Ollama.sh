#!/bin/bash

# Baixa e executa o script de instalação do Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Inicia o servidor Ollama
ollama serve

# Lembrar a execução ---> ./Installing_and_Running_Ollama.sh
# Dar permissão --> chmod +x Installing_and_Running_Ollama.sh
# ollama pull phi3:3.8b
# ollama pull llama2:7b
# ollama pull tinyllama
# ollama pull deepseek-r1:1.5b
# ollama pull deepseek-r1:7b
# ollama list
# ollama run llama3.1:8b

# ollama show llama3.2-vision:11b   <--- para ver as configurações do modelo (quantidade de camadas, etc)

# Fazer --->    sudo systemctl stop ollama


#NOTA:
# sudo lsof -i :8003
# sudo kill -9 <PID>