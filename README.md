# Sistema de Pedidos da Lanchonete

Sistema acadêmico para registrar pedidos de mesas e acompanhar o fluxo de
preparo de uma lanchonete.

O projeto possui duas implementações intercambiáveis do mesmo backend e um
único front-end:

- backend REST organizado segundo o Single Responsibility Principle (SRP);
- backend REST monolítico que viola deliberadamente o SRP para comparação
  acadêmica;
- front-end de página única desenvolvido com React, TypeScript e Vite;
- cardápio fornecido exclusivamente pela API;
- criação, listagem e consulta de pedidos;
- atualização controlada do status dos pedidos;
- tratamento de validações, erros HTTP e indisponibilidade do servidor.

## Estrutura do projeto

```text
LSRP/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
├── backend_sem_srp/
│   ├── tests/
│   │   └── test_api.py
│   ├── main.py
│   ├── README.md
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── relatorio_implementacao_backend_srp.md
├── relatorio_implementacao_backend_sem_srp.md
├── relatorio_implementacao_frontend_lanchonete.md
└── guia_completo_projeto.md
```

As pastas `backend/` e `backend_sem_srp/` expõem o mesmo contrato HTTP. A
diferença é interna: a primeira separa responsabilidades; a segunda concentra
contratos, cardápio, persistência, regras e rotas em `main.py`.

## Tecnologias

### Backend

- Python 3.11 ou superior;
- FastAPI;
- Pydantic;
- Uvicorn;
- pytest;
- armazenamento em memória.

### Front-end

- Node.js 20.19 ou superior;
- React 19;
- TypeScript;
- Vite;
- CSS puro;
- `fetch` nativo;
- npm.

O front-end foi desenvolvido e validado com Node.js `24.19.0`.

## Pré-requisitos

Antes de iniciar, confirme as versões instaladas:

```bash
python --version
node --version
npm --version
```

Caso utilize NVM, a versão validada pode ser ativada com:

```bash
nvm use 24
```

O front-end e **um** dos backends precisam permanecer ativos ao mesmo tempo.
Utilize dois terminais. Não inicie os dois backends simultaneamente, pois ambos
usam a porta `8000`.

## Instalação e execução

### 1. Preparar o ambiente Python

As duas versões possuem as mesmas dependências. Partindo da raiz do projeto,
um único ambiente virtual pode ser usado para ambas:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Em um novo terminal, reative o ambiente antes de iniciar ou testar um backend:

```bash
cd /caminho/para/LSRP
source .venv/bin/activate
```

### 2. Iniciar um backend na porta 8000

Escolha **somente uma** das opções abaixo.

#### Opção A — backend com SRP

Esta é a versão arquiteturalmente recomendada do exemplo:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Opção B — backend sem SRP

Esta é a versão monolítica criada exclusivamente como contraexemplo acadêmico:

```bash
cd backend_sem_srp
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Independentemente da versão escolhida, o backend ficará disponível em:

- API: `http://127.0.0.1:8000`;
- documentação Swagger: `http://127.0.0.1:8000/docs`;
- contrato OpenAPI: `http://127.0.0.1:8000/openapi.json`.

Para confirmar que a API está ativa, acesse:

```text
http://127.0.0.1:8000/api/cardapio
```

A resposta deve conter os seis itens do cardápio.

### 3. Preparar e iniciar o front-end

No segundo terminal, partindo da raiz do projeto:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

O Vite exibirá o endereço local da interface, normalmente:

```text
http://127.0.0.1:5173
```

Abra esse endereço no navegador. O backend precisa continuar ativo no primeiro
terminal.

### 4. Alternar entre as duas versões

O front-end não precisa ser reiniciado nem modificado:

1. no terminal do backend, pressione `Ctrl+C`;
2. entre na pasta da outra implementação;
3. execute o comando Uvicorn correspondente na porta `8000`;
4. recarregue `http://127.0.0.1:5173` no navegador.

Como o armazenamento é apenas em memória, trocar ou reiniciar o backend apaga
os pedidos e reinicia os IDs em `1`.

### 5. Encerrar os servidores

Pressione `Ctrl+C` em cada terminal. Se o Uvicorn informar que a porta `8000`
já está em uso, localize o outro terminal do backend e encerre o processo antes
de tentar novamente.

### Resumo dos processos e endereços

| Processo | Comando | Endereço |
| --- | --- | --- |
| Backend com SRP | `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` dentro de `backend/` | `http://127.0.0.1:8000` |
| Backend sem SRP | `uvicorn main:app --reload --host 127.0.0.1 --port 8000` dentro de `backend_sem_srp/` | `http://127.0.0.1:8000` |
| Front-end | `npm run dev -- --host 127.0.0.1 --port 5173` dentro de `frontend/` | `http://127.0.0.1:5173` |

## Integração entre front-end e backend

Durante o desenvolvimento, o Vite encaminha requisições iniciadas por `/api`
para:

```text
http://127.0.0.1:8000
```

Esse proxy está configurado em `frontend/vite.config.ts` e evita problemas de
CORS durante o desenvolvimento local.

O código do front-end usa endereços relativos, como:

```text
/api/cardapio
/api/pedidos
```

A variável opcional `VITE_API_BASE_URL` permite alterar a base usada pelo
cliente. O valor padrão para desenvolvimento está documentado em
`frontend/.env.example`:

```env
VITE_API_BASE_URL=/api
```

## Funcionalidades disponíveis

### Atendimento

- consultar o cardápio e os preços atuais;
- informar um número de mesa inteiro e positivo;
- selecionar a quantidade de cada item;
- visualizar o total estimado;
- criar um pedido;
- receber a confirmação com o número e o total definitivo do pedido.

### Atendimento e cozinha

- visualizar todos os pedidos;
- consultar um pedido diretamente pelo ID;
- acompanhar mesa, data, itens, quantidades, preços, total e status;
- atualizar o andamento do pedido;
- cancelar pedidos nos estados permitidos.

## Endpoints utilizados

| Método | Rota | Operação |
| --- | --- | --- |
| `GET` | `/api/cardapio` | Consultar o cardápio. |
| `POST` | `/api/pedidos` | Criar um pedido. |
| `GET` | `/api/pedidos` | Listar os pedidos. |
| `GET` | `/api/pedidos/{pedido_id}` | Consultar um pedido. |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | Atualizar o status. |

## Fluxo de status

Todo pedido começa como `RECEBIDO`.

```text
RECEBIDO -> EM_PREPARO -> PRONTO -> ENTREGUE
    |            |
    +-> CANCELADO <-+
```

As ações apresentadas no front-end são:

| Estado atual | Ações disponíveis |
| --- | --- |
| `RECEBIDO` | Iniciar preparo ou cancelar. |
| `EM_PREPARO` | Marcar como pronto ou cancelar. |
| `PRONTO` | Marcar como entregue. |
| `ENTREGUE` | Nenhuma. |
| `CANCELADO` | Nenhuma. |

## Validação do projeto

### Testar o backend com SRP

Com o ambiente virtual Python ativado:

```bash
cd backend
python -m pytest -q
```

### Testar o backend sem SRP

Partindo da raiz e com o mesmo ambiente virtual ativado:

```bash
cd backend_sem_srp
python -m pytest -q
```

### Verificar o front-end

Na pasta `frontend/`:

```bash
npm run lint
npm run build
```

### Roteiro manual recomendado

Com uma das versões do backend e o front-end ativos:

1. confirme que os seis itens do cardápio são apresentados;
2. tente criar um pedido sem mesa e sem itens e verifique as validações;
3. crie um pedido para a mesa `7` com duas unidades do item `1` e uma unidade
   do item `5`;
4. confirme o status `RECEBIDO` e o total definitivo `54.00`;
5. confirme que o pedido aparece na listagem;
6. consulte o pedido pelo ID;
7. avance por `EM_PREPARO`, `PRONTO` e `ENTREGUE`;
8. confirme que um pedido entregue não apresenta novas ações;
9. consulte o ID `999999999` e confirme a mensagem
   `Pedido não encontrado.`;
10. interrompa temporariamente o backend e confirme que o front-end apresenta
    uma mensagem de conexão;
11. teste a interface em larguras de celular e desktop;
12. navegue pelos controles usando a tecla `Tab` e confirme o foco visível.

Na aba Network das ferramentas do navegador, as requisições devem usar
`/api/...` e não devem apresentar erros de CORS.

## Organização do backend com SRP

O backend aplica o Single Responsibility Principle, separando as
responsabilidades entre os módulos:

| Módulo | Responsabilidade |
| --- | --- |
| `models.py` | Entidades e status do domínio. |
| `cardapio.py` | Catálogo fixo de alimentos. |
| `schemas.py` | Contratos e validações HTTP. |
| `repository.py` | Armazenamento em memória e geração de IDs. |
| `service.py` | Casos de uso e regras dos pedidos. |
| `routes.py` | Rotas HTTP e tradução de erros. |
| `main.py` | Criação da aplicação e composição das dependências. |

## Organização do backend sem SRP

O contraexemplo concentra deliberadamente em `backend_sem_srp/main.py`:

- enum e schemas Pydantic;
- cardápio e preços;
- armazenamento em memória e geração de IDs;
- validações, cálculo monetário e regras de negócio;
- transições de status e erros HTTP;
- cinco endpoints e criação da aplicação FastAPI.

O sistema permanece funcional, mas o mesmo módulo passa a ter várias razões
independentes para mudar. Essa concentração caracteriza a violação didática do
SRP; o simples fato de existir um único arquivo, isoladamente, não seria
suficiente para caracterizá-la.

| Necessidade de mudança | Backend com SRP | Backend sem SRP |
| --- | --- | --- |
| Alterar alimento ou preço | `cardapio.py` | `main.py` |
| Trocar armazenamento | `repository.py` | `main.py` |
| Alterar regra de pedido | `service.py` | `main.py` |
| Alterar contrato HTTP | `schemas.py` | `main.py` |
| Alterar endpoint | `routes.py` | `main.py` |
| Alterar composição | `main.py` da versão com SRP | `main.py` monolítico |

## Organização do front-end

| Módulo | Responsabilidade |
| --- | --- |
| `src/types/api.ts` | Tipos equivalentes ao contrato OpenAPI. |
| `src/api/pedidosApi.ts` | Operações HTTP e normalização de erros. |
| `src/components/FormularioPedido.tsx` | Criação e total estimado. |
| `src/components/ConsultaPedido.tsx` | Consulta real pelo ID. |
| `src/components/CartaoPedido.tsx` | Dados e ações de um pedido. |
| `src/components/ListaPedidos.tsx` | Listagem, carregamento, erro e estado vazio. |
| `src/App.tsx` | Estado compartilhado e coordenação dos fluxos. |
| `src/App.css` e `src/index.css` | Interface responsiva e acessível. |

## Características da interface

- página única e responsiva;
- duas colunas em telas largas e uma coluna abaixo de `800px`;
- adaptação de campos e botões abaixo de `480px`;
- cartões separados por bordas, sem sombras ou gradientes;
- ausência de imagens decorativas;
- labels associados aos campos;
- foco de teclado visível;
- mensagens de sucesso e erro acessíveis;
- status sempre acompanhado de texto.

## Observações importantes

- Os pedidos são armazenados somente em memória.
- Reiniciar o backend apaga os pedidos e reinicia a sequência de IDs.
- Somente um backend deve ocupar a porta `8000` por vez.
- As duas versões usam o mesmo front-end e expõem os mesmos cinco endpoints.
- `backend_sem_srp/` é um contraexemplo acadêmico, não uma recomendação de
  arquitetura.
- O cardápio é fornecido pelo backend e não pode ser alterado pelo front-end.
- O total retornado pelo backend é o valor definitivo do pedido.
- O front-end não envia nomes, preços, total, status inicial, ID ou data durante
  a criação.
- O projeto não possui autenticação, pagamentos, estoque ou persistência em
  banco de dados.

## Documentação complementar

- [Guia completo e comentado do projeto](guia_completo_projeto.md)
- [README do backend sem SRP](backend_sem_srp/README.md)
- [Relatório de implementação do backend com SRP](relatorio_implementacao_backend_srp.md)
- [Relatório de implementação do backend sem SRP](relatorio_implementacao_backend_sem_srp.md)
- [Relatório de implementação do front-end](relatorio_implementacao_frontend_lanchonete.md)
