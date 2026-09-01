# Guia de implementação — Front-end de pedidos da lanchonete

## 1. Papel do agente

Você é responsável exclusivamente pelo **front-end** do sistema acadêmico de gerenciamento de pedidos de uma lanchonete. Implemente uma interface web simples, clara e responsiva, integrada ao backend FastAPI existente.

Antes de editar, inspecione o repositório e preserve arquivos e alterações fora desta tarefa. Não altere o backend. Não invente endpoints, campos, status, preços ou regras de negócio.

## 2. Fonte de verdade e regra de parada

Antes de implementar qualquer componente:

1. localize a pasta `backend/`;
2. leia `backend/app/routes.py` e `backend/app/schemas.py`;
3. inicie o backend conforme `backend/README.md`;
4. consulte `http://127.0.0.1:8000/openapi.json`;
5. confirme os cinco endpoints, os corpos e as respostas descritos neste documento.

O backend em execução e seu OpenAPI são a fonte de verdade. Se houver divergência relevante entre eles e este documento, **pare e relate exatamente a diferença**. Não corrija o backend, não adapte silenciosamente o contrato e não crie um contorno no front-end.

## 3. Decisão técnica

Use:

- React;
- TypeScript;
- Vite com o template `react-ts`;
- CSS puro;
- `fetch` nativo para HTTP;
- npm como gerenciador de pacotes.

Não adicione React Router, Axios, Redux, React Query, Tailwind, Bootstrap ou biblioteca de componentes. O sistema possui uma única tela e não precisa dessas dependências.

Crie o projeto na pasta `frontend/`, como irmão de `backend/`:

```text
projeto/
├── backend/
└── frontend/
```

Comando de criação, executado na raiz do projeto:

```bash
npm create vite@latest frontend -- --template react-ts
```

Use uma versão do Node.js aceita pelo Vite instalado. Se o comando informar incompatibilidade, registre a versão atual e atualize o Node antes de continuar; não force a instalação ignorando o aviso.

## 4. Objetivo da interface

A aplicação representa o uso interno da lanchonete:

- o atendente consulta o cardápio e registra um pedido para uma mesa;
- o atendente ou a cozinha visualiza os pedidos;
- a cozinha atualiza o andamento de cada pedido;
- um pedido pode ser consultado pelo ID.

Implemente uma única página chamada **Pedidos da Lanchonete**, contendo:

1. cabeçalho com título e descrição curta;
2. formulário de novo pedido;
3. resumo do valor antes da criação;
4. consulta de pedido por ID;
5. listagem de pedidos;
6. ações de atualização de status.

Não use fotografias, ilustrações, carrosséis ou elementos decorativos desnecessários.

## 5. Contrato obrigatório do backend

### Endpoints

| Método | Rota | Uso no front-end |
| --- | --- | --- |
| `GET` | `/api/cardapio` | Carregar alimentos e preços |
| `POST` | `/api/pedidos` | Criar pedido |
| `GET` | `/api/pedidos` | Listar pedidos |
| `GET` | `/api/pedidos/{pedido_id}` | Consultar pedido por ID |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | Atualizar status |

### Tipos que devem ser espelhados no TypeScript

```ts
export type StatusPedido =
  | 'RECEBIDO'
  | 'EM_PREPARO'
  | 'PRONTO'
  | 'ENTREGUE'
  | 'CANCELADO';

export interface ItemCardapio {
  id: number;
  nome: string;
  preco: string;
}

export interface ItemPedidoSolicitado {
  item_cardapio_id: number;
  quantidade: number;
}

export interface CriacaoPedido {
  numero_mesa: number;
  itens: ItemPedidoSolicitado[];
}

export interface ItemPedidoResposta {
  item_cardapio_id: number;
  nome: string;
  quantidade: number;
  preco_unitario: string;
}

export interface Pedido {
  id: number;
  numero_mesa: number;
  itens: ItemPedidoResposta[];
  status: StatusPedido;
  total: string;
  criado_em: string;
}

export interface AtualizacaoStatus {
  status: StatusPedido;
}
```

Confirme os nomes e tipos no OpenAPI antes de criar essas interfaces. Não use `any` para respostas da API.

### Criação de pedido

Envie somente:

```json
{
  "numero_mesa": 7,
  "itens": [
    {
      "item_cardapio_id": 1,
      "quantidade": 2
    }
  ]
}
```

Nunca envie `nome`, `preco`, `preco_unitario`, `status`, `total`, `id` ou `criado_em`. O backend é responsável por esses valores.

### Erros

O backend pode retornar:

- `400`: item do cardápio inexistente ou transição proibida;
- `404`: pedido inexistente;
- `422`: corpo, campo ou tipo inválido;
- falha de rede: backend indisponível ou endereço incorreto.

O campo `detail` pode ser uma string nos erros de negócio ou uma lista nos erros de validação do FastAPI. O cliente HTTP deve tratar os dois formatos e produzir uma mensagem legível, sem exibir `[object Object]`.

## 6. Integração local sem CORS

Durante o desenvolvimento, o front-end será servido pelo Vite e o backend continuará em `http://127.0.0.1:8000`.

Configure o proxy do Vite em `vite.config.ts`:

- caminho interceptado: `/api`;
- destino: `http://127.0.0.1:8000`;
- `changeOrigin: true`.

No código, faça chamadas relativas como `/api/cardapio` e `/api/pedidos`. Não escreva `http://127.0.0.1:8000` dentro dos componentes.

Se o repositório já possuir uma configuração de ambiente para a URL da API, preserve-a e use uma variável `VITE_API_BASE_URL`, com `/api` como valor local. Evite concatenar `/api` duas vezes.

Não modifique o backend para resolver CORS sem uma solicitação explícita. Se o proxy não puder ser usado, pare e relate a origem exata do front-end que precisaria ser autorizada.

## 7. Estrutura mínima sugerida

Se o front-end ainda não existir, use:

```text
frontend/
├── src/
│   ├── api/
│   │   └── pedidosApi.ts
│   ├── components/
│   │   ├── FormularioPedido.tsx
│   │   ├── ConsultaPedido.tsx
│   │   ├── ListaPedidos.tsx
│   │   └── CartaoPedido.tsx
│   ├── types/
│   │   └── api.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── styles.css
├── .env.example
├── index.html
├── package.json
├── vite.config.ts
└── README.md
```

Não crie componentes de uma ou duas linhas sem responsabilidade própria. Mantenha o estado compartilhado e a coordenação geral em `App.tsx`; mantenha requisições em `pedidosApi.ts` e tipos em `types/api.ts`.

## 8. Requisitos visuais e responsivos

Use uma aparência leve e institucional, sem imagens.

### Paleta

Defina variáveis CSS equivalentes a:

| Uso | Cor |
| --- | --- |
| Fundo da página | `#F6F8F7` |
| Superfícies e cartões | `#FFFFFF` |
| Texto principal | `#1F2937` |
| Texto secundário | `#667085` |
| Verde principal | `#287A55` |
| Verde ao passar o mouse | `#216647` |
| Bordas | `#DDE5E1` |
| Erro | `#B42318` |

Use cores claras nos indicadores de status, sempre acompanhadas do nome textual do status. Não dependa somente da cor para comunicar informação.

### Layout

- largura máxima do conteúdo: aproximadamente `1200px`;
- fundo claro e cartões brancos com borda discreta;
- em telas largas, formulário e pedidos podem ocupar duas colunas;
- abaixo de aproximadamente `800px`, use uma coluna;
- abaixo de `480px`, botões e campos devem ocupar a largura disponível;
- evite rolagem horizontal;
- use espaçamento consistente e alvos de interação confortáveis;
- mantenha foco de teclado visível e `label` associado a cada campo.

Não use gradientes, excesso de sombras ou animações elaboradas.

## 9. Comportamento da tela

### Cardápio e formulário

- Carregue o cardápio exclusivamente de `GET /api/cardapio`.
- Não replique no front-end os seis nomes ou preços.
- Exiba nome, preço em reais e campo de quantidade para cada item.
- A quantidade inicial deve ser `0`.
- O número da mesa deve ser inteiro e maior que zero.
- Envie apenas itens cuja quantidade seja maior que zero.
- Bloqueie o envio se nenhum item tiver sido selecionado.
- Exiba um total estimado calculado a partir dos preços recebidos do backend.
- O total devolvido no pedido criado é o valor definitivo.
- Durante o envio, desabilite o botão para evitar criação duplicada.
- Após sucesso, limpe o formulário, informe o número do pedido e atualize a lista.

Use `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })` somente para apresentação. Não altere as strings monetárias recebidas nem as envie de volta ao backend.

### Pedidos

Cada cartão deve mostrar:

- número do pedido;
- número da mesa;
- data e hora formatadas em `pt-BR`;
- itens, quantidades e preços unitários;
- total;
- status textual;
- ações permitidas para o estado atual.

Use estas ações, sem inventar transições:

| Estado atual | Ações exibidas |
| --- | --- |
| `RECEBIDO` | `Iniciar preparo` → `EM_PREPARO`; `Cancelar` → `CANCELADO` |
| `EM_PREPARO` | `Marcar como pronto` → `PRONTO`; `Cancelar` → `CANCELADO` |
| `PRONTO` | `Marcar como entregue` → `ENTREGUE` |
| `ENTREGUE` | Nenhuma |
| `CANCELADO` | Nenhuma |

Se uma atualização retornar erro, mantenha o estado atual, mostre a mensagem do backend e recarregue a lista para sincronizar a interface.

### Consulta por ID

- Aceite apenas ID inteiro positivo.
- Use `GET /api/pedidos/{pedido_id}`.
- Exiba o resultado no mesmo formato de cartão.
- Para `404`, mostre `Pedido não encontrado.` sem apagar a listagem geral.

### Estados obrigatórios

Trate separadamente:

- carregamento inicial;
- carregamento de uma ação;
- lista vazia;
- erro de conexão;
- erro de validação;
- sucesso na criação ou atualização.

Mensagens de sucesso e erro devem usar uma região com `aria-live`. Não use `alert()` do navegador.

## 10. Passo a passo de implementação

### Etapa 1 — Verificar o backend

- Execute as cinco verificações da seção 2.
- Faça uma requisição real ao cardápio e confirme os campos.
- Não avance se o backend não iniciar ou se o contrato divergir.

### Etapa 2 — Criar o projeto

- Gere o template React + TypeScript.
- Remova apenas os arquivos demonstrativos do Vite que não serão usados.
- Não altere `backend/`.

### Etapa 3 — Configurar a integração

- Configure o proxy `/api` no Vite.
- Crie `.env.example` sem segredos.
- Valide no navegador que `GET /api/cardapio` passa pelo proxy e retorna `200`.

### Etapa 4 — Definir tipos e cliente HTTP

- Espelhe os schemas confirmados no OpenAPI.
- Centralize as cinco operações em `pedidosApi.ts`.
- Verifique `response.ok` antes de interpretar sucesso.
- Normalize erros `400`, `404`, `422` e falhas de rede.
- Não esconda erros com dados simulados.

### Etapa 5 — Construir a base visual

- Crie cabeçalho, contêiner, cartões, campos e botões.
- Implemente as variáveis CSS e os pontos de quebra.
- Verifique a página em larguras de celular e desktop.

### Etapa 6 — Implementar o novo pedido

- Carregue o cardápio pela API.
- Controle mesa e quantidades no React.
- Monte exatamente o corpo `CriacaoPedido`.
- Envie, trate a resposta e atualize a lista.

### Etapa 7 — Implementar listagem, consulta e status

- Liste os pedidos retornados pelo backend.
- Implemente busca por ID sem filtrar localmente a lista.
- Exiba apenas ações válidas para cada status.
- Após atualização, substitua os dados pelo retorno do backend e sincronize a lista.

### Etapa 8 — Revisar estados e acessibilidade

- Teste carregamento, vazio, sucesso, erro HTTP e erro de rede.
- Verifique navegação por teclado, foco, labels e mensagens.
- Garanta que nenhuma informação dependa apenas de cor.

### Etapa 9 — Validar a integração

Com o backend e o front-end em execução:

1. carregue os seis itens do cardápio;
2. crie um pedido para a mesa `7`, com duas unidades do item `1` e uma do item `5`;
3. confirme HTTP `201`, status `RECEBIDO` e total `54.00`;
4. confirme que o pedido aparece na listagem;
5. consulte o mesmo pedido pelo ID;
6. avance para `EM_PREPARO`, `PRONTO` e `ENTREGUE`;
7. confirme que não há ação disponível após `ENTREGUE`;
8. consulte um ID inexistente e confirme o tratamento do `404`;
9. desligue temporariamente o backend e confirme a mensagem de conexão;
10. verifique no console e na aba Network que não existem erros de CORS, rotas duplicadas ou corpos divergentes.

Execute também:

```bash
npm run lint
npm run build
```

Não declare a integração como concluída se qualquer uma dessas verificações falhar.

### Etapa 10 — Documentar

No `frontend/README.md`, registre:

- tecnologias utilizadas;
- requisito de Node.js;
- instalação com `npm install`;
- execução com `npm run dev`;
- necessidade de manter o backend ativo;
- funcionamento do proxy `/api`;
- comandos de lint e build;
- estrutura dos principais módulos.

## 11. Fora do escopo

Não implemente:

- autenticação ou usuários;
- cadastro ou alteração do cardápio;
- cadastro de mesas ou clientes;
- pagamento, estoque ou entrega externa;
- edição completa ou exclusão de pedidos;
- imagens de alimentos;
- modo escuro;
- gráficos, relatórios ou painel administrativo;
- persistência no navegador como substituição do backend;
- dados falsos quando a API estiver indisponível;
- deploy ou modificação do backend.

## 12. Critérios de aceite

A tarefa estará concluída somente quando:

- o front-end consumir os cinco endpoints reais;
- nenhum alimento, preço ou pedido estiver hardcoded;
- os corpos enviados corresponderem exatamente ao OpenAPI;
- valores controlados pelo backend nunca forem enviados na criação;
- o proxy local funcionar sem erro de CORS;
- todos os estados e erros obrigatórios tiverem tratamento visível;
- as ações respeitarem exatamente as transições do backend;
- a interface funcionar sem rolagem horizontal em celular e desktop;
- a aplicação tiver labels, foco visível e mensagens acessíveis;
- `npm run lint` e `npm run build` terminarem sem erros;
- a validação integrada da etapa 9 for concluída;
- nenhum arquivo do backend tiver sido alterado.

## 13. Entrega do agente

Ao finalizar:

1. liste os arquivos criados ou alterados;
2. informe como o contrato real do backend foi verificado;
3. informe os comandos executados e seus resultados reais;
4. descreva o teste integrado realizado;
5. registre qualquer divergência encontrada;
6. não afirme que a integração funciona sem backend e front-end terem sido executados juntos.
