# Relatório da implementação do backend SRP

## Resumo

Foi implementado um backend REST em Python para gerenciamento de pedidos de
uma lanchonete. A API permite consultar o cardápio, criar pedidos, consultar e
listar pedidos e atualizar seus status.

A implementação está em `backend/` e utiliza FastAPI, Pydantic, armazenamento
em memória, `Decimal` para valores monetários e pytest para os testes.

Não foi implementado front-end nem qualquer funcionalidade fora do escopo do
guia.

## Arquivos implementados

| Arquivo | Implementação |
| --- | --- |
| `backend/app/models.py` | Entidades de domínio: `ItemCardapio`, `ItemPedido`, `Pedido` e `StatusPedido`. |
| `backend/app/cardapio.py` | Cardápio fixo com os seis alimentos e preços definidos. |
| `backend/app/schemas.py` | Contratos HTTP de entrada e saída, com validações Pydantic. |
| `backend/app/repository.py` | Repositório em memória, geração sequencial de IDs, listagem e busca. |
| `backend/app/service.py` | Casos de uso, regras de negócio, cálculo de totais e transições de status. |
| `backend/app/routes.py` | Cinco endpoints `/api` e conversão de erros de domínio para HTTP. |
| `backend/app/main.py` | Criação da aplicação FastAPI e composição das dependências. |
| `backend/tests/test_pedido_service.py` | Testes das regras e casos de uso do serviço. |
| `backend/tests/test_pedidos_api.py` | Testes dos contratos e endpoints HTTP. |
| `backend/requirements.txt` | Dependências necessárias para executar a API e os testes. |
| `backend/README.md` | Instruções de instalação, execução, testes e responsabilidades dos módulos. |
| `backend/pytest.ini` | Configuração para que o comando `pytest` encontre o pacote `app`. |

## Endpoints atendidos

Todos os endpoints exigidos foram implementados com o prefixo `/api`:

| Método | Rota | Status de sucesso |
| --- | --- | --- |
| `GET` | `/api/cardapio` | `200` |
| `POST` | `/api/pedidos` | `201` |
| `GET` | `/api/pedidos` | `200` |
| `GET` | `/api/pedidos/{pedido_id}` | `200` |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | `200` |

O OpenAPI da aplicação foi verificado e contém somente esses cinco endpoints de
negócio.

## Regras seguidas e atendidas

### Cardápio

- O cardápio contém exatamente seis itens:
  - Hambúrguer — `20.00`;
  - X-Salada — `23.00`;
  - Cachorro-quente — `15.00`;
  - Misto-quente — `12.00`;
  - Batata frita — `14.00`;
  - Porção de nuggets — `16.00`.
- Os nomes e preços são obtidos pelo backend a partir do ID do cardápio.
- Não existe endpoint para alterar o cardápio.
- Os preços são retornados como strings com exatamente duas casas decimais.

### Criação de pedidos

- Todo pedido começa com status `RECEBIDO`.
- O número da mesa deve ser um inteiro positivo.
- A lista de itens não pode ser vazia.
- A quantidade deve ser um inteiro positivo.
- O ID do cardápio deve ser um inteiro; se não existir, a API retorna `400` com
  `Item do cardápio não encontrado.`.
- Campos calculados ou controlados pelo backend, como `id`, `nome`,
  `preco_unitario`, `status`, `total` e `criado_em`, não são aceitos no corpo de
  criação.
- Campos extras também são rejeitados dentro dos itens.
- Uma criação inválida não salva o pedido nem consome o próximo ID.
- Itens repetidos são preservados na ordem recebida, pois o guia não definiu
  uma regra de agregação.

### Valores monetários e data

- Os cálculos usam `Decimal` e valores de preço criados a partir de strings.
- O total é normalizado para duas casas decimais.
- Quantidades grandes não recebem um limite inventado; a precisão local do
  cálculo é dimensionada para manter o resultado exato.
- `criado_em` é gerado com data/hora UTC consciente de fuso.
- `preco`, `preco_unitario` e `total` são serializados como strings com duas
  casas decimais.

### Consulta e listagem

- A listagem retorna `[]` quando não há pedidos.
- Os pedidos são listados em ordem crescente de ID.
- Um pedido inexistente retorna `404` com `Pedido não encontrado.`.

### Transições de status

As transições implementadas são exatamente:

```text
RECEBIDO   -> EM_PREPARO ou CANCELADO
EM_PREPARO -> PRONTO ou CANCELADO
PRONTO     -> ENTREGUE
ENTREGUE   -> nenhum estado
CANCELADO  -> nenhum estado
```

Além disso:

- Solicitar novamente o status atual é idempotente.
- `ENTREGUE` e `CANCELADO` são estados finais.
- Transições proibidas retornam `400` com `Transição de status não permitida.`.
- Uma tentativa de atualizar pedido inexistente retorna `404`.
- Status inválidos ou corpos com campos extras permanecem como `422`, seguindo
  a validação padrão do FastAPI.

## Princípio implementado: Single Responsibility Principle

O princípio aplicado foi o **Single Responsibility Principle (SRP)**, ou
Princípio da Responsabilidade Única.

Cada módulo possui uma responsabilidade coesa e uma razão principal para
mudar:

- `models.py` muda quando a representação do domínio muda.
- `cardapio.py` muda quando o catálogo fixo muda.
- `schemas.py` muda quando o contrato HTTP ou suas validações mudam.
- `repository.py` muda quando a forma de persistir os pedidos muda.
- `service.py` muda quando as regras de negócio mudam.
- `routes.py` muda quando as rotas ou o mapeamento HTTP mudam.
- `main.py` muda quando a composição da aplicação muda.

As rotas não calculam preços, não geram IDs e não decidem transições. O
repositório não valida requisições nem conhece HTTP. O serviço não importa
FastAPI. Essa separação demonstra que as responsabilidades não foram
concentradas em uma única classe ou módulo.

## Verificação de correção

A implementação foi verificada com:

```bash
cd /home/brunodf/LSRP/backend
.venv/bin/python -m pytest -q
```

Resultado real:

```text
53 passed in 0.39s
```

Também foram executadas as seguintes verificações:

- Importação de `app.main:app`: **OK**.
- `pip check`: **nenhuma dependência quebrada**.
- Inicialização do Uvicorn: **concluída com sucesso**.
- Requisição real a `GET /api/cardapio`: **HTTP 200**, com os seis itens
  esperados.
- Bateria adicional com 130 requisições HTTP e 202 asserções: **sem falhas**.

## Conclusão

Sim, o backend foi implementado corretamente em relação ao guia. Os cinco
endpoints obrigatórios, o cardápio fixo, as regras de validação, o fluxo de
status, os códigos de erro, a serialização monetária, o uso de UTC, os testes e
a separação por responsabilidade foram atendidos.

Os dados são mantidos somente em memória durante a execução do processo. Ao
reiniciar a aplicação, os pedidos são descartados e a sequência de IDs começa
novamente em `1`, conforme o escopo solicitado.
