@echo off
echo 🦕 DINO SDK - Build Script v2.3.0
echo ======================================

echo 📦 Mudando para diretório do projeto...
cd "c:\Users\User\OneDrive\Documentos\Projetos\Data_Master_2025\GIT\dino_2\dino_sdk"

echo 🔧 Limpando build anterior...
if exist build rmdir /s /q build
if exist dino_sdk.egg-info rmdir /s /q dino_sdk.egg-info

echo 🏗️  Gerando novo wheel...
python setup.py bdist_wheel

echo 📋 Listando arquivos gerados...
dir dist\*.whl

echo.
echo ✅ Build concluído!
echo 📍 Localização do arquivo:
echo    %CD%\dist\dino_sdk-2.3.0-py3-none-any.whl
echo.
echo 🚀 Para instalar no Databricks:
echo    1. Faça upload do arquivo .whl para o cluster
echo    2. Execute: %%pip install /FileStore/wheels/dino_sdk-2.3.0-py3-none-any.whl --force-reinstall
echo.
pause
