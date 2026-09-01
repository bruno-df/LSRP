# Sistema de Pedidos da Lanchonete

Sistema acadêmico para registrar pedidos de mesas e acompanhar o fluxo de
preparo de uma lanchonete.

O projeto possui:

- backend REST desenvolvido com FastAPI;
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
│   ├── README.md
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── types/
│   ├── README.md
│   ├── package.json
│   └── vite.config.ts
├── relatorio_implementacao_backend_srp.md
└── relatorio_implementacao_frontend_lanchonete.md
```

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

O backend e o front-end precisam permanecer ativos ao mesmo tempo. Utilize dois
terminais separados para executar o sistema.

## Instalação e execução

### 1. Preparar e iniciar o backend

No primeiro terminal, partindo da raiz do projeto:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

O backend ficará disponível em:

- API: `http://127.0.0.1:8000`;
- documentação Swagger: `http://127.0.0.1:8000/docs`;
- contrato OpenAPI: `http://127.0.0.1:8000/openapi.json`.

Para confirmar que a API está ativa, acesse:

```text
http://127.0.0.1:8000/api/cardapio
```

A resposta deve conter os seis itens do cardápio.

### 2. Preparar e iniciar o front-end

No segundo terminal, partindo da raiz do projeto:

```bash
cd frontend
npm install
npm run dev
```

O Vite exibirá o endereço local da interface, normalmente:

```text
http://127.0.0.1:5173
```

Abra esse endereço no navegador. O backend precisa continuar ativo no primeiro
terminal.

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

### Testar o backend

Com o ambiente virtual do backend ativado:

```bash
cd backend
python -m pytest
```

### Verificar o front-end

Na pasta `frontend/`:

```bash
npm run lint
npm run build
```

### Roteiro manual recomendado

Com backend e front-end ativos:

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

## Organização do backend

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
- O cardápio é fornecido pelo backend e não pode ser alterado pelo front-end.
- O total retornado pelo backend é o valor definitivo do pedido.
- O front-end não envia nomes, preços, total, status inicial, ID ou data durante
  a criação.
- O projeto não possui autenticação, pagamentos, estoque ou persistência em
  banco de dados.

## Documentação complementar

- [README do backend](backend/README.md)
- [README do front-end](frontend/README.md)
- [Relatório de implementação do backend](relatorio_implementacao_backend_srp.md)
- [Relatório de implementação do front-end](relatorio_implementacao_frontend_lanchonete.md)
