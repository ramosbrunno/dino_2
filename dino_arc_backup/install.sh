#!/bin/bash

# Script de instalação do Dino ARC CLI
# Execute este script para instalar o Dino ARC como comando global

set -e

echo "🚀 Instalando Dino ARC CLI..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale pip primeiro."
    exit 1
fi

# Atualizar pip
echo "📦 Atualizando pip..."
pip3 install --upgrade pip

# Instalar o pacote em modo desenvolvimento
echo "📦 Instalando Dino ARC..."
pip3 install -e .

# Verificar instalação
echo "✅ Verificando instalação..."
if command -v dino-arc &> /dev/null; then
    echo "🎉 Dino ARC CLI instalado com sucesso!"
    echo ""
    echo "📋 Comandos disponíveis:"
    echo "  dino-arc --help                 # Ver ajuda"
    echo "  dino-arc --action init --projeto test  # Inicializar"
    echo "  dino-arc --action plan --projeto test  # Planejar"
    echo "  dino-arc --action apply --projeto test # Criar recursos"
    echo ""
    echo "📚 Para mais exemplos, veja: EXEMPLOS_CLI.md"
else
    echo "❌ Falha na instalação. Verifique os logs acima."
    exit 1
fi

echo "🎯 Instalação concluída!"
