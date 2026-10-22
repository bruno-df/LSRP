#!/usr/bin/env python3
"""Script de inicialização do backend do projeto LSRP.

Detecta o sistema operacional, configura o ambiente virtual, pergunta qual
backend usar (com ou sem SRP) e inicia o servidor uvicorn.
Funciona em Windows, Linux e macOS.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Cores ANSI para o terminal
# ──────────────────────────────────────────────────────────────────────────────

VERDE = "\033[92m"
AZUL = "\033[94m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CIANO = "\033[96m"
NEGRITO = "\033[1m"
RESET = "\033[0m"

# ──────────────────────────────────────────────────────────────────────────────
# Caminhos do projeto
# ──────────────────────────────────────────────────────────────────────────────

RAIZ = Path(__file__).resolve().parent
VENV_DIR = RAIZ / ".venv"
BACKEND_SRP_DIR = RAIZ / "backend"
BACKEND_SEM_SRP_DIR = RAIZ / "backend_sem_srp"

PORTA_BACKEND = 8000

# ──────────────────────────────────────────────────────────────────────────────
# Detecção de sistema operacional
# ──────────────────────────────────────────────────────────────────────────────

SISTEMA = platform.system()  # "Windows", "Linux" ou "Darwin"

if SISTEMA == "Windows":
    PYTHON_VENV = VENV_DIR / "Scripts" / "python.exe"
    PIP_VENV = VENV_DIR / "Scripts" / "pip.exe"
else:
    PYTHON_VENV = VENV_DIR / "bin" / "python"
    PIP_VENV = VENV_DIR / "bin" / "pip"


def banner() -> None:
    """Exibe o banner de boas-vindas."""

    print(f"""
{CIANO}{NEGRITO}╔══════════════════════════════════════════════════╗
║          🍔  LSRP — Lanchonete Startup  🍔       ║
╚══════════════════════════════════════════════════╝{RESET}
{AMARELO}  Sistema detectado: {NEGRITO}{SISTEMA}{RESET}
""")


def criar_venv() -> None:
    """Cria o ambiente virtual se ainda não existir."""

    if PYTHON_VENV.exists():
        print(f"{VERDE}✔ Ambiente virtual já existe em {VENV_DIR.name}/{RESET}")
        return

    print(f"{AMARELO}⏳ Criando ambiente virtual em {VENV_DIR.name}/...{RESET}")
    subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        check=True,
    )
    print(f"{VERDE}✔ Ambiente virtual criado.{RESET}")


def instalar_dependencias_python(requirements: Path) -> None:
    """Instala as dependências Python a partir de um requirements.txt."""

    print(f"{AMARELO}⏳ Instalando dependências Python ({requirements.parent.name})...{RESET}")
    subprocess.run(
        [str(PIP_VENV), "install", "-r", str(requirements), "-q"],
        check=True,
    )
    print(f"{VERDE}✔ Dependências Python instaladas.{RESET}")


def escolher_backend() -> tuple[str, Path, str]:
    """Pergunta ao usuário qual backend iniciar.

    Retorna uma tupla (nome, diretório, módulo uvicorn).
    """

    print(f"""{NEGRITO}Qual backend deseja iniciar?{RESET}

  {CIANO}[1]{RESET} Backend {NEGRITO}com SRP{RESET}    (backend/)
  {CIANO}[2]{RESET} Backend {NEGRITO}sem SRP{RESET}   (backend_sem_srp/)
""")

    while True:
        escolha = input(f"{AZUL}➜ Digite 1 ou 2: {RESET}").strip()
        if escolha == "1":
            return ("com SRP", BACKEND_SRP_DIR, "app.main:app")
        if escolha == "2":
            return ("sem SRP", BACKEND_SEM_SRP_DIR, "main:app")
        print(f"{VERMELHO}  Opção inválida. Tente novamente.{RESET}")


def exibir_links(nome_backend: str) -> None:
    """Mostra os links do servidor e dica do frontend no terminal."""

    print(f"""
{VERDE}{NEGRITO}══════════════════════════════════════════════════
  ✅  Backend iniciado com sucesso!
══════════════════════════════════════════════════{RESET}

  {CIANO}🔧 Backend ({nome_backend}):{RESET}
     {NEGRITO}http://127.0.0.1:{PORTA_BACKEND}{RESET}
     {NEGRITO}http://127.0.0.1:{PORTA_BACKEND}/docs{RESET}  (Swagger)

{AMARELO}  💡 Para iniciar o frontend, abra outro terminal e execute:{RESET}
     {NEGRITO}cd frontend && npm run dev{RESET}

{AMARELO}  Pressione Ctrl+C para encerrar o servidor.{RESET}
""")


def iniciar_backend(diretorio: Path, modulo: str) -> None:
    """Inicia o uvicorn no terminal atual (bloqueante)."""

    cmd = [
        str(PYTHON_VENV), "-m", "uvicorn",
        modulo,
        "--host", "127.0.0.1",
        "--port", str(PORTA_BACKEND),
        "--reload",
    ]
    subprocess.run(cmd, cwd=str(diretorio))


def main() -> None:
    """Função principal do script de inicialização."""

    banner()

    # 1. Ambiente virtual
    criar_venv()

    # 2. Escolha do backend
    nome_backend, diretorio_backend, modulo_backend = escolher_backend()

    # 3. Dependências Python
    requirements = diretorio_backend / "requirements.txt"
    instalar_dependencias_python(requirements)

    # 4. Exibir links e dica do frontend
    exibir_links(nome_backend)

    # 5. Iniciar o backend (bloqueante — Ctrl+C para parar)
    iniciar_backend(diretorio_backend, modulo_backend)


if __name__ == "__main__":
    # Habilita cores ANSI no terminal do Windows
    if SISTEMA == "Windows":
        os.system("")  # Ativa suporte a ANSI no cmd/PowerShell

    main()
