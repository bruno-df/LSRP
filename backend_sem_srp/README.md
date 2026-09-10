# Backend sem SRP — contraexemplo acadêmico

Esta é uma implementação alternativa e deliberadamente monolítica da API de
pedidos da lanchonete. Ela preserva o contrato HTTP do backend original para
mostrar que um sistema pode funcionar corretamente e, ainda assim, apresentar
alto acoplamento interno e várias razões para modificar o mesmo módulo.

O código é material didático. A organização de `main.py` não deve ser tomada
como referência arquitetural para um sistema real.

## Instalação e execução

Partindo da raiz do projeto:

```bash
cd backend_sem_srp
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

A API estará disponível em `http://127.0.0.1:8000`; o Swagger, em `/docs`; e o
OpenAPI, em `/openapi.json`.

Somente um backend pode usar a porta `8000` por vez. Para alternar, pare o
Uvicorn em execução e inicie uma destas opções:

```bash
# Versão com SRP, a partir da raiz
cd backend
uvicorn app.main:app --reload --port 8000

# Versão sem SRP, a partir da raiz
cd backend_sem_srp
uvicorn main:app --reload --port 8000
```

O front-end permanece funcionalmente inalterado e continua usando `/api` por
meio do proxy do Vite. Basta mantê-lo em execução e recarregar a página após
trocar o backend.

## Testes

Com o ambiente virtual ativado, dentro de `backend_sem_srp/`:

```bash
pytest -q
```

A suíte cobre cardápio, criação, validações, IDs, listagem, consulta, erros,
transições, idempotência, estados finais, precisão monetária e OpenAPI. Cada
teste começa com o armazenamento vazio e o contador de IDs reiniciado.

## Armazenamento temporário

Os pedidos são mantidos somente em um dicionário global em memória. Todos os
dados são perdidos quando o processo termina. Esta versão não compartilha
estado, objetos ou módulos com `backend/`.

## Responsabilidades concentradas

O mesmo `main.py` contém:

- o enum de status e os schemas Pydantic;
- o cardápio e os preços;
- o dicionário de pedidos e a geração de IDs;
- as validações e regras de negócio;
- o cálculo e a serialização de valores monetários;
- as transições de status;
- os erros e endpoints HTTP;
- a criação da aplicação FastAPI.

Isso dá ao mesmo módulo razões diferentes para mudar. Uma alteração de preço,
persistência, regra, contrato ou rota exige editar o mesmo lugar, aumentando o
acoplamento e o risco de impacto entre responsabilidades.

| Necessidade de mudança | Backend com SRP | Backend sem SRP |
| --- | --- | --- |
| Alterar alimento ou preço | `cardapio.py` | `main.py` |
| Trocar armazenamento | `repository.py` | `main.py` |
| Alterar regra de pedido | `service.py` | `main.py` |
| Alterar contrato HTTP | `schemas.py` | `main.py` |
| Alterar endpoint | `routes.py` | `main.py` |
| Alterar composição | `main.py` próprio da versão correta | `main.py` monolítico |

Um único arquivo não viola automaticamente o Single Responsibility Principle.
A violação deliberada deste contraexemplo ocorre porque o mesmo módulo concentra
responsabilidades que possuem razões independentes para mudar. O sistema segue
funcional e compatível com o front-end, porém sua estrutura possui maior
acoplamento e tende a ser mais difícil de manter.
