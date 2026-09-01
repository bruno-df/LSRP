# Relatório da implementação do backend sem SRP

## 1. Resumo

Foi implementado em `backend_sem_srp/` um backend alternativo para o sistema de
pedidos da lanchonete. Ele preserva o contrato HTTP e o comportamento do
backend existente, mas concentra deliberadamente responsabilidades diferentes
em um único `main.py`.

A finalidade é acadêmica: demonstrar que um sistema pode responder
corretamente e, mesmo assim, possuir uma estrutura com alto acoplamento e
maior dificuldade de manutenção.

Nenhuma funcionalidade de front-end foi implementada nessa etapa. O front-end
original continua sendo usado sem alteração e escolhe indiretamente o backend
por meio do processo que estiver ocupando a porta `8000`.

## 2. Arquivos implementados

| Arquivo | Conteúdo |
| --- | --- |
| `backend_sem_srp/main.py` | Aplicação monolítica com schemas, cardápio, estado, regras, erros e rotas. |
| `backend_sem_srp/tests/test_api.py` | Testes isolados do contrato e das regras observáveis. |
| `backend_sem_srp/requirements.txt` | Dependências da API e dos testes. |
| `backend_sem_srp/pytest.ini` | Configuração mínima para importar `main.py` durante os testes. |
| `backend_sem_srp/README.md` | Instalação, execução, alternância, testes e explicação didática. |

Não foram criadas pastas ou camadas de `models`, `schemas`, `services`,
`repositories`, `routes` ou `cardapio`. A ausência dessas separações é
intencional nesta versão.

## 3. Proteção e independência das versões

As seguintes regras de isolamento foram seguidas:

- `backend/` não foi refatorado, renomeado ou usado por importação;
- `frontend/` e seu proxy não foram alterados para selecionar a versão;
- `backend_sem_srp/` não compartilha armazenamento nem objetos com
  `backend/`;
- cada processo mantém seu próprio estado somente em memória;
- nenhum ambiente virtual foi copiado para a nova pasta;
- nenhuma funcionalidade fora do escopo foi adicionada;
- não foram criados commits nem removidos arquivos alheios à tarefa.

A auditoria final com `git diff -- backend frontend` não encontrou alterações
rastreadas nessas duas pastas.

## 4. Contrato HTTP preservado

Foram implementadas somente as cinco operações de negócio previstas:

| Método | Rota | Sucesso |
| --- | --- | --- |
| `GET` | `/api/cardapio` | HTTP `200` |
| `POST` | `/api/pedidos` | HTTP `201` |
| `GET` | `/api/pedidos` | HTTP `200` |
| `GET` | `/api/pedidos/{pedido_id}` | HTTP `200` |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | HTTP `200` |

Os schemas de entrada proíbem campos extras. Os schemas de saída preservam os
nomes, tipos, enumerações e formatos observados no OpenAPI da versão com SRP.

## 5. Regras seguidas e atendidas

### 5.1 Cardápio

| Regra | Situação |
| --- | --- |
| Expor exatamente seis itens | Atendida |
| Preservar IDs, nomes e preços definidos | Atendida |
| Retornar preços como strings com duas casas | Atendida |
| Obter nomes e preços no backend, nunca do cliente | Atendida |
| Não criar atualização de cardápio | Atendida |

O cardápio implementado contém Hambúrguer (`20.00`), X-Salada (`23.00`),
Cachorro-quente (`15.00`), Misto-quente (`12.00`), Batata frita (`14.00`) e
Porção de nuggets (`16.00`).

### 5.2 Criação e armazenamento de pedidos

| Regra | Situação |
| --- | --- |
| `numero_mesa` inteiro e positivo | Atendida por validação Pydantic estrita |
| Pelo menos um item por pedido | Atendida |
| `quantidade` inteira e positiva | Atendida por validação Pydantic estrita |
| Todo pedido começa em `RECEBIDO` | Atendida |
| IDs sequenciais iniciando em `1` | Atendida |
| Pedido inválido não consome ID | Atendida |
| Itens repetidos preservados e na mesma ordem | Atendida |
| Estado apenas durante a execução | Atendida com dicionário global em memória |
| Listagem vazia retorna `[]` | Atendida |
| Listagem em ordem crescente de ID | Atendida |

O corpo de criação aceita somente `numero_mesa`, `itens`,
`item_cardapio_id` e `quantidade`. Dados controlados pelo servidor, como ID,
nome, preço, total, status e data, são rejeitados quando enviados como campos
extras.

### 5.3 Valores monetários e data

- preços e totais são calculados com `Decimal`;
- a precisão local é ajustada para manter quantidades inteiras grandes exatas;
- `preco`, `preco_unitario` e `total` são strings com duas casas decimais;
- `criado_em` usa data e hora UTC consciente de fuso;
- a serialização substitui `+00:00` por `Z`, preservando o contrato original.

### 5.4 Status dos pedidos

As transições implementadas são:

```text
RECEBIDO   -> EM_PREPARO ou CANCELADO
EM_PREPARO -> PRONTO ou CANCELADO
PRONTO     -> ENTREGUE
ENTREGUE   -> nenhum estado
CANCELADO  -> nenhum estado
```

Repetir o status atual é idempotente. `ENTREGUE` e `CANCELADO` são estados
finais.

### 5.5 Erros

| Condição | Resposta |
| --- | --- |
| Item inexistente | HTTP `400`, `Item do cardápio não encontrado.` |
| Transição proibida | HTTP `400`, `Transição de status não permitida.` |
| Pedido inexistente | HTTP `404`, `Pedido não encontrado.` |
| Formato, campo ou tipo inválido | HTTP `422` do FastAPI |

### 5.6 Funcionalidades deliberadamente não adicionadas

Não foram implementados autenticação, banco de dados, estoque, pagamento,
entrega, cadastro de clientes, alteração do cardápio ou qualquer mecanismo no
front-end para escolher o backend.

## 6. Princípio deliberadamente não implementado

O princípio não aplicado nesta versão é o **Single Responsibility Principle
(SRP)**, ou Princípio da Responsabilidade Única, o primeiro princípio do grupo
SOLID.

O SRP propõe que um módulo tenha uma responsabilidade coesa e uma razão
principal para mudar. No contraexemplo, o mesmo `main.py` muda por razões
independentes:

- mudança de alimento ou preço;
- mudança de persistência ou geração de IDs;
- mudança de contrato HTTP;
- mudança de validação ou regra de pedido;
- mudança no cálculo monetário;
- mudança de transição de status;
- mudança de endpoint ou tratamento HTTP;
- mudança na composição da aplicação.

Um arquivo único não representa automaticamente uma violação do SRP. A
violação ocorre aqui porque responsabilidades com motivos diferentes para
mudar foram conscientemente agrupadas no mesmo módulo e manipuladas
diretamente pelas funções de rota.

## 7. Comparação arquitetural

| Necessidade de mudança | Backend com SRP | Backend sem SRP |
| --- | --- | --- |
| Alterar alimento ou preço | `cardapio.py` | `main.py` |
| Trocar armazenamento | `repository.py` | `main.py` |
| Alterar regra de pedido | `service.py` | `main.py` |
| Alterar contrato HTTP | `schemas.py` | `main.py` |
| Alterar endpoint | `routes.py` | `main.py` |
| Alterar composição | `main.py` próprio da versão com SRP | `main.py` monolítico |

Na versão com SRP, as rotas coordenam HTTP e delegam as regras. Na versão sem
SRP, as rotas acessam diretamente o cardápio e o dicionário global, calculam o
total, decidem transições, atualizam o estado e lançam `HTTPException`.

## 8. Testes e verificações executadas

### 8.1 Suítes automatizadas

Backend com SRP:

```bash
cd backend
../.venv/bin/pytest -q
```

Resultado registrado:

```text
53 passed in 0.38s
```

Backend sem SRP:

```bash
cd backend_sem_srp
../.venv/bin/pytest -q
```

Resultado registrado:

```text
44 passed in 0.33s
```

A suíte monolítica reinicia o dicionário e o contador de IDs antes de cada
teste. Ela não importa a implementação com SRP.

### 8.2 Comparação observável

As duas versões foram iniciadas separadamente com Uvicorn na porta `8000`. Uma
matriz de 22 cenários HTTP foi executada contra ambas, cobrindo:

- cardápio e listagem vazia;
- criação válida, item inexistente e campo extra;
- preservação de itens repetidos, totais e IDs;
- consulta existente, inexistente e ID de formato inválido;
- atualização de pedido inexistente e status inválido;
- transições permitidas, proibidas e idempotentes;
- estados finais `ENTREGUE` e `CANCELADO`.

Após normalizar somente o valor dinâmico de `criado_em`, os códigos HTTP e os
corpos dos 22 cenários foram idênticos. O OpenAPI completo diferiu apenas no
título da aplicação, diferença expressamente permitida pelo guia.

### 8.3 Integração com o front-end original

O backend sem SRP foi iniciado na porta `8000` e o Vite original na porta
`5173`. Pelo proxy real `/api` foram confirmados:

- carregamento do HTML do front-end com HTTP `200`;
- carregamento dos seis itens do cardápio;
- criação e consulta de um pedido;
- fluxo `RECEBIDO -> EM_PREPARO -> PRONTO -> ENTREGUE`;
- ausência de necessidade de modificar o proxy ou o código-fonte do front-end.

Também foram executados com sucesso:

```bash
cd frontend
npm run lint
npm run build
```

A automação da interação visual no navegador não foi concluída porque o
controlador visual disponível no ambiente não iniciou. Portanto, a validação
visual de botões, mensagens e renderização deve ser confirmada manualmente pelo
roteiro do `README.md`; ela não é apresentada neste relatório como executada.

## 9. Como iniciar o sistema

Prepare uma vez o ambiente na raiz:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

No primeiro terminal, escolha um backend:

```bash
# Com SRP
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Ou, em vez dele, sem SRP
cd backend_sem_srp
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

No segundo terminal:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Abra `http://127.0.0.1:5173`. Somente um backend pode usar a porta `8000` por
vez. Para alternar, encerre o Uvicorn atual com `Ctrl+C`, inicie a outra versão
e recarregue a página.

## 10. Conclusão

O contraexemplo atende ao contrato e às regras funcionais solicitadas, mas não
aplica deliberadamente o SRP. Essa diferença permite comparar duas estruturas
internas por trás da mesma API e do mesmo front-end: uma com responsabilidades
separadas e outra funcional, porém mais acoplada e com várias razões para
alterar o mesmo módulo.

O material deve ser usado para estudo e comparação, não como recomendação para
organizar aplicações FastAPI em produção.
