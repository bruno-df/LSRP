# Backend de pedidos da lanchonete

API REST acadêmica para registrar pedidos de mesas e acompanhar o trabalho da
cozinha. A organização dos módulos demonstra o Single Responsibility Principle
(SRP), mantendo contratos HTTP, regras de negócio e armazenamento separados.

## Ambiente e instalação

É necessário Python 3.11 ou superior. A partir desta pasta (`backend`), execute:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Executar

Inicie a API, ainda na pasta `backend`, com:

```bash
uvicorn app.main:app --reload
```

A documentação interativa ficará disponível em `http://127.0.0.1:8000/docs`.
Os cinco endpoints usam o prefixo `/api`:

| Método | Rota | Operação |
| --- | --- | --- |
| `GET` | `/api/cardapio` | Consultar o cardápio |
| `POST` | `/api/pedidos` | Criar um pedido |
| `GET` | `/api/pedidos` | Listar os pedidos |
| `GET` | `/api/pedidos/{pedido_id}` | Consultar um pedido |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | Atualizar o status |

## Testar

```bash
python -m pytest
```

## Responsabilidades dos módulos

| Módulo | Responsabilidade |
| --- | --- |
| `models.py` | Representar as entidades e os status do domínio |
| `cardapio.py` | Manter e consultar o cardápio fixo |
| `schemas.py` | Validar e serializar os contratos HTTP |
| `repository.py` | Armazenar pedidos em memória e gerar seus IDs |
| `service.py` | Executar os casos de uso e regras dos pedidos |
| `routes.py` | Expor as rotas e traduzir erros para HTTP |
| `main.py` | Criar a aplicação e conectar suas dependências |

## Cardápio e fluxo dos pedidos

O cardápio é fixo e contém Hambúrguer (`20.00`), X-Salada (`23.00`),
Cachorro-quente (`15.00`), Misto-quente (`12.00`), Batata frita (`14.00`) e
Porção de nuggets (`16.00`). Nomes e preços são obtidos pelo backend e não
podem ser alterados pela API.

Todo pedido começa como `RECEBIDO`. As transições permitidas são:

```text
RECEBIDO -> EM_PREPARO -> PRONTO -> ENTREGUE
    |            |
    +-> CANCELADO <-+
```

Repetir o status atual não altera o pedido. `ENTREGUE` e `CANCELADO` são estados
finais.

Os pedidos ficam somente na memória do processo. Ao reiniciar a aplicação,
todos os dados são descartados e a sequência de IDs volta a começar em `1`.
