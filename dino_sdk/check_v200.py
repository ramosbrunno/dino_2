import subprocess
import sys

# Instalar v2.0.0
print("🔧 Instalando v2.0.0...")
result = subprocess.run([
    sys.executable, "-m", "pip", "install", 
    "dist/dino_sdk-2.0.0-py3-none-any.whl", 
    "--force-reinstall"
], capture_output=True, text=True)

print("📦 STDOUT:")
print(result.stdout)
print("❌ STDERR:")
print(result.stderr)
print(f"🎯 Return Code: {result.returncode}")

# Verificar versão
try:
    from dino_sdk import __version__
    print(f"✅ DINO SDK v{__version__} funcionando!")
except Exception as e:
    print(f"❌ Erro import: {e}")
