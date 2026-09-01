# Guia de implementação — Backend de pedidos de lanchonete com SRP

## 1. Papel do agente

Você é responsável exclusivamente pelo **backend** de um sistema acadêmico e pequeno de gerenciamento de pedidos de uma lanchonete. Implemente uma API REST em Python que demonstre claramente o **Single Responsibility Principle (SRP)**.

Trabalhe somente com os requisitos deste documento. Antes de editar, inspecione o repositório e preserve arquivos, convenções e alterações que não pertençam a esta tarefa. Não implemente o front-end.

## 2. Resultado esperado

Entregar um backend funcional, simples de executar e testar, no qual um atendente registre pedidos para mesas e a cozinha acompanhe seu andamento. Cada módulo deve ter uma responsabilidade coesa e uma razão clara para mudar.

Use como base:

- Python 3.11 ou superior;
- FastAPI para a API HTTP;
- Pydantic para os contratos de entrada e saída;
- armazenamento em memória durante a execução;
- pytest para os testes.

Não adicione banco de dados, autenticação, mensageria, serviços externos ou infraestrutura de implantação.

## 3. Escopo funcional obrigatório

O sistema deve permitir somente:

1. consultar o cardápio fixo;
2. criar um pedido para uma mesa;
3. listar todos os pedidos, em ordem crescente de ID;
4. consultar um pedido pelo ID;
5. atualizar o status de um pedido.

### Cardápio fixo

| ID | Alimento | Preço |
| --- | --- | ---: |
| `1` | Hambúrguer | `20.00` |
| `2` | X-Salada | `23.00` |
| `3` | Cachorro-quente | `15.00` |
| `4` | Misto-quente | `12.00` |
| `5` | Batata frita | `14.00` |
| `6` | Porção de nuggets | `16.00` |

O cardápio pertence ao backend e não pode ser alterado pela API.

### Dados enviados para um item do pedido

- `item_cardapio_id`: ID inteiro de um alimento existente no cardápio;
- `quantidade`: número inteiro maior que zero.

### Dados de um pedido

- `id`: inteiro positivo gerado pelo repositório;
- `numero_mesa`: número inteiro maior que zero;
- `itens`: lista com pelo menos um item;
- cada item retornado contém `item_cardapio_id`, `nome`, `quantidade` e `preco_unitario`;
- `status`: `RECEBIDO`, `EM_PREPARO`, `PRONTO`, `ENTREGUE` ou `CANCELADO`;
- `total`: soma de `quantidade × preco_unitario` de todos os itens;
- `criado_em`: data e hora UTC com fuso horário.

Use `Decimal` nos cálculos monetários e normalize o total para duas casas decimais. Não use `float` para calcular valores financeiros.

## 4. Regras de negócio

- Todo pedido novo começa com status `RECEBIDO`.
- O backend deve obter o nome e o preço de cada alimento por meio do `item_cardapio_id`; esses valores nunca vêm do cliente da API.
- O número da mesa deve ser positivo.
- Um pedido deve possuir pelo menos um item.
- A quantidade de cada item deve ser positiva.
- Um `item_cardapio_id` inexistente deve produzir HTTP `400` com a mensagem `Item do cardápio não encontrado.`.
- A requisição de criação não pode informar `id`, `nome`, `preco_unitario`, `status`, `total` ou `criado_em`.
- Transições permitidas:
  - `RECEBIDO` → `EM_PREPARO` ou `CANCELADO`;
  - `EM_PREPARO` → `PRONTO` ou `CANCELADO`;
  - `PRONTO` → `ENTREGUE`.
- `ENTREGUE` e `CANCELADO` são estados finais.
- Solicitar o status atual novamente deve ser uma operação idempotente e retornar o pedido sem alteração.
- Pedido inexistente deve produzir HTTP `404`.
- Transição de status não permitida deve produzir HTTP `400`.
- Erros de formato ou validação da requisição devem permanecer como HTTP `422`, seguindo o comportamento do FastAPI.

## 5. Contrato da API

Use o prefixo `/api` e implemente apenas estes endpoints:

| Método | Rota | Resultado |
| --- | --- | --- |
| `GET` | `/api/cardapio` | Retorna os seis alimentos e preços com HTTP `200` |
| `POST` | `/api/pedidos` | Cria e retorna o pedido com HTTP `201` |
| `GET` | `/api/pedidos` | Retorna a lista de pedidos com HTTP `200` |
| `GET` | `/api/pedidos/{pedido_id}` | Retorna um pedido com HTTP `200` ou `404` |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | Atualiza apenas o status e retorna HTTP `200`, `400` ou `404` |

O endpoint do cardápio retorna uma lista de objetos com os campos `id`, `nome` e `preco`. O campo `preco` deve ser uma string com duas casas decimais.

### Corpo para criação

```json
{
  "numero_mesa": 7,
  "itens": [
    {
      "item_cardapio_id": 1,
      "quantidade": 2
    },
    {
      "item_cardapio_id": 5,
      "quantidade": 1
    }
  ]
}
```

### Corpo para atualização do status

```json
{
  "status": "EM_PREPARO"
}
```

### Resposta de pedido

```json
{
  "id": 1,
  "numero_mesa": 7,
  "itens": [
    {
      "item_cardapio_id": 1,
      "nome": "Hambúrguer",
      "quantidade": 2,
      "preco_unitario": "20.00"
    },
    {
      "item_cardapio_id": 5,
      "nome": "Batata frita",
      "quantidade": 1,
      "preco_unitario": "14.00"
    }
  ],
  "status": "RECEBIDO",
  "total": "54.00",
  "criado_em": "2026-09-01T18:00:00Z"
}
```

Serialize `preco`, `preco_unitario` e `total` como strings com exatamente duas casas decimais para manter o contrato previsível para o front-end.

Para erros definidos pelo sistema, use mensagens diretas no formato padrão do FastAPI, por exemplo:

```json
{
  "detail": "Pedido não encontrado."
}
```

## 6. Estrutura mínima

Se o repositório estiver vazio, use esta estrutura. Se já existir uma estrutura Python equivalente, adapte os nomes sem duplicar camadas.

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── cardapio.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   └── routes.py
├── tests/
│   ├── test_pedido_service.py
│   └── test_pedidos_api.py
├── requirements.txt
└── README.md
```

### Responsabilidade de cada módulo

| Módulo | Única responsabilidade |
| --- | --- |
| `models.py` | Representar `ItemCardapio`, `Pedido`, `ItemPedido` e `StatusPedido` no domínio |
| `cardapio.py` | Manter e consultar os seis alimentos e seus preços fixos |
| `schemas.py` | Definir e validar os contratos HTTP de entrada e saída |
| `repository.py` | Armazenar, gerar IDs, listar e localizar pedidos em memória |
| `service.py` | Executar os casos de uso e aplicar as regras de negócio dos pedidos |
| `routes.py` | Receber requisições, chamar o serviço e converter resultados ou erros em respostas HTTP |
| `main.py` | Criar a aplicação e conectar suas dependências e rotas |

Não divida cada método em uma classe diferente. SRP exige responsabilidades coesas, não o maior número possível de arquivos ou classes.

## 7. Passo a passo de implementação

### Etapa 1 — Inspecionar o projeto

- Verifique a estrutura, dependências e padrões existentes.
- Não altere nem remova arquivos alheios ao backend de pedidos.
- Se houver conflito entre este documento e uma decisão já consolidada no repositório, pare e registre o conflito antes de implementar.

### Etapa 2 — Preparar o esqueleto mínimo

- Crie somente os módulos ausentes da estrutura definida.
- Declare apenas as dependências realmente usadas.
- Garanta que a aplicação possa ser iniciada a partir de `app.main:app` dentro da pasta `backend`.

### Etapa 3 — Modelar o domínio

- Defina o enum de status e as estruturas de item do cardápio, pedido e item do pedido.
- Mantenha detalhes de HTTP e armazenamento fora deste módulo.
- Use tipos explícitos e data/hora UTC consciente de fuso.

### Etapa 4 — Implementar o cardápio

- Cadastre somente os seis alimentos e preços definidos neste documento.
- Permita listar o cardápio e localizar um alimento pelo ID.
- Não aceite alterações no cardápio durante a execução.
- Mantenha requisições HTTP e regras do fluxo de pedidos fora deste módulo.

### Etapa 5 — Implementar o repositório em memória

- Armazene pedidos por ID.
- Gere IDs inteiros sequenciais a partir de `1`.
- Implemente somente salvar, listar e buscar por ID.
- Não coloque validação de requisição, regra de transição ou resposta HTTP aqui.

### Etapa 6 — Implementar o serviço

- Receba o repositório e o cardápio pelo construtor.
- Centralize neste módulo a criação do pedido, a validação dos IDs do cardápio, o cálculo do total, a consulta e a mudança de status.
- Crie erros específicos e simples para item do cardápio inexistente, pedido inexistente e transição inválida.
- Não importe FastAPI no serviço.

### Etapa 7 — Definir os schemas HTTP

- Crie modelos distintos para item do cardápio, criação do pedido, item solicitado, atualização de status e resposta do pedido.
- Restrinja campos extras nas requisições para impedir dados não previstos.
- Faça as validações estruturais com Pydantic e mantenha as regras de fluxo no serviço.
- Garanta a serialização monetária com duas casas decimais.

### Etapa 8 — Criar as rotas e compor a aplicação

- Implemente apenas os cinco endpoints especificados.
- As rotas de pedidos devem delegar ao serviço, e a rota de cardápio deve delegar ao módulo de cardápio.
- Converta os erros conhecidos do serviço em `HTTPException` com os códigos definidos.
- Não procure preços, não calcule total, não gere ID e não implemente transições diretamente nas rotas.
- Instancie o cardápio, o repositório e o serviço uma única vez para manter os dados durante a execução.
- Registre as rotas na aplicação FastAPI.
- Use um título curto e descritivo para a documentação automática.
- Não configure CORS sem que o projeto existente ou a integração real do front-end exija origens específicas.

### Etapa 9 — Testar

Crie testes independentes e determinísticos. Cada teste deve receber armazenamento vazio.

No serviço, cubra pelo menos:

- criação com status inicial e total correto;
- preço obtido do cardápio pelo backend;
- item do cardápio inexistente;
- consulta de pedido inexistente;
- transição permitida;
- transição proibida;
- repetição idempotente do status atual.

Na API, cubra pelo menos:

- listagem dos seis itens do cardápio;
- criação com HTTP `201` e formato esperado;
- listagem em ordem de ID;
- consulta inexistente com HTTP `404`;
- requisição inválida com HTTP `422`;
- mudança de status válida e inválida.

### Etapa 10 — Documentar e verificar

No `README.md`, informe:

- objetivo do backend;
- requisitos de ambiente;
- instalação das dependências;
- comando para iniciar a API;
- comando para executar os testes;
- tabela curta das responsabilidades dos módulos;
- descrição do cardápio fixo e do fluxo de status;
- observação de que os dados existem apenas enquanto o processo estiver em execução.

Adicione comentários ou docstrings somente para esclarecer a responsabilidade de uma classe/módulo ou uma regra não óbvia. Evite comentários que apenas repitam o código.

Execute os testes e confirme que a aplicação importa e inicia sem erros antes de encerrar.

## 8. Restrições de escopo

Não implemente:

- front-end ou arquivos visuais;
- cadastro de clientes, mesas ou novos itens de cardápio;
- alteração de nomes ou preços do cardápio pela API;
- estoque, pagamento real ou rastreamento de entregas;
- descontos, cupons ou impostos;
- login, usuários ou permissões;
- banco de dados ou migrações;
- envio de e-mail ou notificações;
- Docker, CI/CD ou deploy;
- padrões, abstrações ou bibliotecas sem uso concreto neste escopo.

Não crie funcionalidades extras para “completar” o sistema. Se um detalhe indispensável não estiver definido, registre a dúvida em vez de inventar um requisito.

## 9. Critérios de aceite

A tarefa estará concluída somente quando:

- os cinco endpoints funcionarem conforme o contrato;
- o cardápio tiver exatamente os seis alimentos e preços definidos;
- a criação aceitar apenas número da mesa, IDs do cardápio e quantidades;
- todas as regras de negócio estiverem no serviço, e não nas rotas ou no repositório;
- cada módulo cumprir a responsabilidade declarada;
- valores monetários forem calculados com `Decimal` e retornados com duas casas decimais;
- erros `400`, `404` e `422` forem distinguíveis;
- os testes passarem sem depender da ordem de execução;
- o README permitir que outra pessoa instale, execute e teste o backend;
- nenhum arquivo de front-end ou funcionalidade fora do escopo for criado.

## 10. Entrega do agente

Ao finalizar:

1. apresente uma lista curta dos arquivos criados ou alterados;
2. explique em uma frase a responsabilidade de cada módulo;
3. informe os comandos executados para validação e seus resultados reais;
4. registre qualquer decisão necessária que não estivesse explícita;
5. não afirme que algo funciona sem ter executado a verificação correspondente.
