# Relatório da implementação do front-end da lanchonete

## 1. Resumo

Foi implementado um front-end web para o sistema acadêmico de gerenciamento de
pedidos da lanchonete. A aplicação permite consultar o cardápio, criar pedidos
para uma mesa, visualizar a listagem de pedidos, consultar um pedido pelo ID e
atualizar seu status de acordo com as regras do backend.

A implementação está localizada em `frontend/` e utiliza React, TypeScript,
Vite, CSS puro, `fetch` nativo e npm. O front-end foi integrado ao backend
FastAPI existente por meio do proxy de desenvolvimento do Vite.

O projeto foi mantido em uma única página, conforme solicitado. Não foram
adicionadas bibliotecas de roteamento, gerenciamento global de estado,
requisições HTTP, CSS utilitário ou componentes visuais externos.

O backend não foi modificado durante a implementação.

## 2. Tecnologias utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| React `19.2.8` | Componentização, estado e renderização da interface. |
| TypeScript `6.0.2` | Tipagem dos componentes, estados, propriedades e contrato da API. |
| Vite `8.2.2` | Ambiente de desenvolvimento, proxy local e build de produção. |
| CSS puro | Layout, responsividade, estados visuais e foco de teclado. |
| `fetch` nativo | Comunicação com os cinco endpoints do backend. |
| npm | Instalação de dependências e execução dos scripts. |
| Oxlint | Verificação estática do código-fonte. |

A implementação e as validações foram executadas com Node.js `24.19.0`.

## 3. Arquivos implementados

| Arquivo | Responsabilidade |
| --- | --- |
| `frontend/src/types/api.ts` | Tipos TypeScript equivalentes aos schemas confirmados no OpenAPI. |
| `frontend/src/api/pedidosApi.ts` | Cliente HTTP, cinco operações da API e normalização de erros. |
| `frontend/src/components/FormularioPedido.tsx` | Formulário de criação, quantidades, validações e total estimado. |
| `frontend/src/components/ConsultaPedido.tsx` | Formulário de consulta real pelo ID do pedido. |
| `frontend/src/components/CartaoPedido.tsx` | Exibição completa do pedido e ações permitidas para o status atual. |
| `frontend/src/components/ListaPedidos.tsx` | Listagem e estados de carregamento, erro e lista vazia. |
| `frontend/src/App.tsx` | Estado compartilhado, carregamento inicial e coordenação dos fluxos. |
| `frontend/src/App.css` | Estilos dos componentes, cartões, formulários e responsividade. |
| `frontend/src/index.css` | Variáveis de cor, estilos globais e configurações de acessibilidade. |
| `frontend/src/main.tsx` | Inicialização da aplicação React. |
| `frontend/vite.config.ts` | Plugin React e proxy `/api` para o backend local. |
| `frontend/.env.example` | Exemplo da variável `VITE_API_BASE_URL` com valor local `/api`. |
| `frontend/index.html` | Documento principal, idioma `pt-BR`, título e descrição. |
| `frontend/package.json` | Dependências e scripts `dev`, `lint`, `build` e `preview`. |
| `frontend/package-lock.json` | Versões resolvidas das dependências npm. |
| `frontend/README.md` | Instalação, execução, proxy, comandos e estrutura dos módulos. |
| `frontend/.oxlintrc.json` | Regras de lint para React e TypeScript. |
| `frontend/tsconfig.json` | Configuração principal do TypeScript. |
| `frontend/tsconfig.app.json` | Configuração TypeScript da aplicação. |
| `frontend/tsconfig.node.json` | Configuração TypeScript dos arquivos executados pelo Node.js. |
| `frontend/.gitignore` | Exclusão de dependências, build, logs e arquivos locais. |

Os arquivos demonstrativos do template Vite que não eram utilizados foram
removidos. O front-end final não referencia imagens, ícones demonstrativos ou
conteúdo do template inicial.

## 4. Verificação do contrato do backend

Antes da implementação foram realizadas as verificações exigidas pelo guia:

1. a pasta `backend/` foi localizada;
2. `backend/app/routes.py` foi lido;
3. `backend/app/schemas.py` foi lido;
4. as instruções de `backend/README.md` foram verificadas;
5. o backend foi executado;
6. `http://127.0.0.1:8000/openapi.json` foi consultado;
7. uma requisição real foi feita para `GET /api/cardapio`.

O OpenAPI confirmou os cinco endpoints exigidos:

| Método | Rota | Uso no front-end |
| --- | --- | --- |
| `GET` | `/api/cardapio` | Carregar alimentos e preços. |
| `POST` | `/api/pedidos` | Criar um pedido. |
| `GET` | `/api/pedidos` | Listar pedidos. |
| `GET` | `/api/pedidos/{pedido_id}` | Consultar um pedido pelo ID. |
| `PATCH` | `/api/pedidos/{pedido_id}/status` | Atualizar o status. |

A chamada real ao cardápio retornou HTTP `200`, seis itens e os campos `id`,
`nome` e `preco` com os tipos previstos.

Não foi encontrada divergência relevante entre o guia, as rotas, os schemas,
o OpenAPI e as respostas reais do backend.

## 5. Requisitos técnicos seguidos

### 5.1 Estrutura e dependências

- O projeto foi criado em `frontend/`, como irmão de `backend/`.
- Foi utilizado o template React com TypeScript do Vite.
- O gerenciador utilizado foi o npm.
- Foi utilizado CSS puro.
- Todas as chamadas HTTP usam `fetch` nativo.
- O sistema permanece em uma única página.
- Não foram adicionados React Router, Axios, Redux, React Query, Tailwind,
  Bootstrap ou bibliotecas de componentes.
- Não foi utilizada persistência no navegador como substituição do backend.
- Não foram criados dados simulados para esconder indisponibilidade da API.

### 5.2 Tipagem do contrato

Foram criados os tipos:

- `StatusPedido`;
- `ItemCardapio`;
- `ItemPedidoSolicitado`;
- `CriacaoPedido`;
- `ItemPedidoResposta`;
- `Pedido`;
- `AtualizacaoStatus`.

Os tipos refletem os nomes de campos e formatos confirmados no OpenAPI. Não foi
utilizado `any` para as respostas da API.

### 5.3 Integração local

O proxy do Vite foi configurado com:

- caminho interceptado: `/api`;
- destino: `http://127.0.0.1:8000`;
- `changeOrigin: true`.

O cliente utiliza chamadas relativas, como `/api/cardapio` e `/api/pedidos`.
Não existe endereço absoluto do backend dentro dos componentes.

A base da API pode ser configurada com `VITE_API_BASE_URL`. Na ausência dessa
variável, o cliente utiliza `/api` e remove barras finais para evitar rotas
duplicadas.

## 6. Funcionalidades implementadas

### 6.1 Carregamento inicial

Ao iniciar, a aplicação carrega cardápio e pedidos em operações independentes.
Cada área possui seu próprio estado de carregamento e erro.

Foi utilizado `AbortController` para cancelar requisições do carregamento
inicial quando o componente é desmontado, evitando atualizações tardias de
estado.

### 6.2 Novo pedido

O formulário implementa:

- campo para o número da mesa;
- carregamento do cardápio exclusivamente pelo backend;
- nome e preço de cada item recebido;
- campo de quantidade para cada item;
- quantidade inicial `0`;
- validação de mesa inteira e maior que zero;
- bloqueio quando nenhum item foi selecionado;
- envio somente de itens com quantidade maior que zero;
- cálculo do total estimado;
- formatação monetária em `pt-BR` somente para apresentação;
- bloqueio do botão durante o envio;
- limpeza da mesa e das quantidades após sucesso;
- mensagem informando o ID e o total definitivo;
- atualização da listagem usando a resposta real do backend.

O corpo enviado na criação contém exclusivamente:

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

O front-end não envia `id`, `nome`, `preco`, `preco_unitario`, `status`,
`total` ou `criado_em`.

### 6.3 Listagem de pedidos

Cada cartão apresenta:

- número do pedido;
- número da mesa;
- data e hora formatadas em `pt-BR`;
- itens, quantidades e preços unitários;
- total do pedido;
- status textual;
- ações permitidas para o estado atual.

A listagem possui estados distintos para carregamento, erro e ausência de
pedidos.

### 6.4 Consulta pelo ID

A consulta:

- aceita somente ID inteiro positivo;
- executa `GET /api/pedidos/{pedido_id}`;
- não filtra localmente a listagem;
- mostra o resultado no mesmo componente de cartão;
- apresenta `Pedido não encontrado.` quando o backend retorna `404`;
- não apaga nem substitui a listagem geral.

### 6.5 Atualização de status

Foram implementadas exatamente as ações permitidas:

| Estado atual | Ações disponíveis |
| --- | --- |
| `RECEBIDO` | `Iniciar preparo` e `Cancelar`. |
| `EM_PREPARO` | `Marcar como pronto` e `Cancelar`. |
| `PRONTO` | `Marcar como entregue`. |
| `ENTREGUE` | Nenhuma. |
| `CANCELADO` | Nenhuma. |

As transições enviadas são:

```text
RECEBIDO   -> EM_PREPARO ou CANCELADO
EM_PREPARO -> PRONTO ou CANCELADO
PRONTO     -> ENTREGUE
```

Durante a atualização, os controles do pedido correspondente são desabilitados.
Um conjunto de IDs em atualização impede requisições duplicadas para o mesmo
pedido e permite controlar corretamente operações simultâneas em pedidos
diferentes.

Em caso de erro no `PATCH`:

- o status apresentado não é alterado de forma otimista;
- a mensagem do backend é exibida;
- a listagem é recarregada;
- o pedido consultado também é sincronizado quando corresponde a um item da
  listagem atualizada.

## 7. Tratamento de erros e estados

O cliente verifica `response.ok` antes de interpretar uma resposta como
sucesso.

Foram tratados:

- HTTP `400` para item inexistente ou transição proibida;
- HTTP `404` para pedido inexistente;
- HTTP `422` para erros de validação;
- falhas de rede;
- resposta JSON inválida;
- carregamento inicial;
- carregamento de criação, consulta e atualização;
- listagem vazia;
- sucesso na criação;
- sucesso na consulta;
- sucesso na atualização.

O campo `detail` é normalizado quando contém uma string ou uma lista de objetos
de validação do FastAPI. As localizações e mensagens são combinadas em texto
legível, evitando a exibição de `[object Object]`.

A mensagem utilizada para falhas de rede é:

```text
Não foi possível conectar ao servidor. Verifique se o backend está ativo.
```

## 8. Interface, responsividade e acessibilidade

### 8.1 Padrão visual

Foi adotada uma aparência simples, leve e institucional:

- fundo `#F6F8F7`;
- superfícies brancas;
- texto principal `#1F2937`;
- texto secundário `#667085`;
- verde principal `#287A55`;
- verde de interação `#216647`;
- bordas discretas;
- vermelho `#B42318` para erros.

Não foram utilizados:

- `box-shadow` ou `text-shadow`;
- gradientes;
- fotografias ou ilustrações;
- imagens de alimentos;
- carrosséis;
- animações elaboradas;
- modo escuro;
- elementos decorativos sem função.

Os cartões são separados por bordas e espaçamento, atendendo à solicitação de
evitar características visuais associadas a interfaces geradas por IA.

### 8.2 Responsividade

- O conteúdo possui largura máxima de aproximadamente `1200px`.
- Em telas largas, formulário e pedidos são apresentados em duas colunas.
- Abaixo de `800px`, a interface utiliza uma coluna.
- Abaixo de `480px`, busca, ações e campos utilizam a largura disponível.
- Foram utilizados `minmax(0, ...)`, `min-width: 0`, quebra de texto e wrapping
  para reduzir risco de rolagem horizontal.
- A largura mínima suportada pela página é `320px`.

### 8.3 Acessibilidade

- Todos os campos possuem `label` associado.
- Erros específicos utilizam `aria-describedby` quando aplicável.
- Campos inválidos utilizam `aria-invalid`.
- Mensagens usam regiões `aria-live`, `role="status"` ou `role="alert"`.
- O estado de atualização usa `aria-busy`.
- O foco de teclado possui contorno visível e contrastante.
- Os status são apresentados por texto e cor; nenhuma informação depende
  somente da cor.
- Os cartões usam `useId()` para manter IDs DOM únicos mesmo quando o mesmo
  pedido aparece na consulta e na listagem.
- Datas usam elementos `<time>` com o valor ISO original.
- Não foi utilizado `alert()` do navegador.

## 9. Funcionalidades mantidas fora do escopo

Conforme solicitado, não foram implementados:

- autenticação ou usuários;
- cadastro ou edição do cardápio;
- cadastro de mesas ou clientes;
- pagamentos;
- estoque;
- entrega externa;
- edição completa ou exclusão de pedidos;
- imagens;
- modo escuro;
- gráficos ou relatórios operacionais;
- painel administrativo;
- persistência local como substituição do backend;
- dados falsos quando a API está indisponível;
- deploy;
- alterações no backend.

## 10. Verificações executadas

### 10.1 Instalação

Foi executado:

```bash
npm install
```

Resultado:

```text
27 pacotes instalados
0 vulnerabilidades encontradas
```

### 10.2 Lint

Foi executado na pasta `frontend/`:

```bash
npm run lint
```

Resultado: concluído sem avisos ou erros.

### 10.3 Build

Foi executado:

```bash
npm run build
```

Resultado real da execução final:

```text
22 módulos transformados
build concluído sem erros
```

### 10.4 Testes do backend

Para confirmar que o backend continuava íntegro, foi executado:

```bash
cd /home/brunodf/LSRP/backend
/home/brunodf/LSRP/.venv/bin/python -m pytest
```

Resultado real:

```text
53 passed in 0.40s
```

### 10.5 Teste integrado pelo proxy do front-end

Com backend e Vite em execução simultaneamente, o fluxo foi testado por
`http://127.0.0.1:5173/api`:

1. `GET /api/cardapio` retornou HTTP `200` e os seis itens;
2. foi criado um pedido para a mesa `7` com duas unidades do item `1` e uma
   unidade do item `5`;
3. o `POST` retornou HTTP `201`, status `RECEBIDO` e total `54.00`;
4. o pedido criado recebeu ID `3` naquele processo do backend;
5. a listagem retornou HTTP `200` e continha o pedido;
6. a consulta pelo ID retornou HTTP `200` e o mesmo pedido;
7. a atualização para `EM_PREPARO` retornou HTTP `200`;
8. a atualização para `PRONTO` retornou HTTP `200`;
9. a atualização para `ENTREGUE` retornou HTTP `200`;
10. uma transição inválida após `ENTREGUE` retornou HTTP `400` com
    `Transição de status não permitida.`;
11. a consulta ao ID `999999999` retornou HTTP `404` com
    `Pedido não encontrado.`;
12. um corpo inválido retornou HTTP `422` com `detail` em formato de lista.

Também foi executado um teste controlado sobre o módulo transformado pelo Vite.
O teste confirmou:

- transformação da lista de validações `422` em mensagem textual;
- preservação do status HTTP dentro de `ErroApi`;
- mensagem legível para falha de rede.

### 10.6 Auditoria estática visual

Foi verificada a ausência de:

- sombras;
- gradientes;
- `background-image`;
- tags `<img>`;
- imagens referenciadas por `url()`;
- dados do cardápio hardcoded nos arquivos da aplicação;
- bibliotecas proibidas no `package.json`.

## 11. Matriz de atendimento dos requisitos

| Requisito | Situação | Evidência |
| --- | --- | --- |
| React, TypeScript e Vite | Atendido | Dependências, configuração e build concluído. |
| CSS puro | Atendido | Estilos em `App.css` e `index.css`. |
| `fetch` nativo | Atendido | Cliente centralizado em `pedidosApi.ts`. |
| Cinco endpoints reais | Atendido | OpenAPI confirmado e fluxo integrado executado. |
| Cardápio obtido do backend | Atendido | `GET /api/cardapio`, sem itens hardcoded. |
| Corpo de criação exato | Atendido | Envio somente de mesa, ID do item e quantidade. |
| Total estimado e definitivo | Atendido | Estimativa no formulário e total real na resposta. |
| Consulta real pelo ID | Atendido | `GET /api/pedidos/{pedido_id}`. |
| Transições exatas de status | Atendido | Mapeamento por status e testes HTTP realizados. |
| Erros `400`, `404`, `422` | Atendido | Cliente normaliza string e lista de detalhes. |
| Falha de rede | Atendido | Mensagem específica e teste controlado do cliente. |
| Estados de carregamento | Atendido | Cardápio, listagem, criação, consulta e atualização. |
| Lista vazia | Atendido | Estado dedicado em `ListaPedidos`. |
| Mensagens acessíveis | Atendido | `aria-live`, `status` e `alert`. |
| Labels e foco visível | Atendido | Labels associados e foco contrastante. |
| Responsividade no CSS | Atendido | Breakpoints em `800px` e `480px`. |
| Ausência de sombras e imagens | Atendido | Auditoria estática sem ocorrências. |
| Proxy sem URL absoluta nos componentes | Atendido | Proxy Vite e base relativa `/api`. |
| `npm run lint` | Atendido | Executado sem erros. |
| `npm run build` | Atendido | Executado sem erros. |
| Backend não alterado | Atendido | Nenhum arquivo-fonte do backend foi editado. |
| Validação visual automatizada no navegador | Atendido com ressalva | O controle de navegador disponível não iniciou; fontes, build e fluxo HTTP foram verificados. |

## 12. Ressalvas e limitações da validação

A integração disponível para controle automatizado do navegador falhou durante
a inicialização. Por esse motivo, não foi possível concluir uma rodada
automatizada de cliques, inspeção visual e redimensionamento dentro do
navegador.

Essa limitação não impediu:

- a execução simultânea do backend e do Vite;
- a verificação do proxy;
- a compilação dos módulos servidos pelo Vite;
- o teste real dos cinco endpoints pelo endereço do front-end;
- o teste completo de criação, listagem, consulta e status;
- o lint e o build;
- a auditoria estática de responsividade e acessibilidade.

Ainda assim, recomenda-se uma conferência visual manual final no navegador em
larguras próximas de `375px`, `800px` e `1200px`, além de uma navegação completa
por teclado. As instruções de instalação e execução estão documentadas em
`frontend/README.md`, e a conferência pode ser iniciada com `npm run dev`.

## 13. Conclusão

A implementação do front-end atende aos requisitos funcionais, técnicos, de
integração, organização, tratamento de erros, acessibilidade e estilo definidos
no guia.

Foram implementados os cinco fluxos reais da API, o formulário de criação, o
total estimado, a listagem, a consulta por ID, as transições de status, os
estados obrigatórios, a normalização de erros, o proxy local e a documentação.

Os comandos `npm run lint` e `npm run build` foram concluídos sem erros. O fluxo
integrado executado pelo proxy confirmou criação com HTTP `201` e total
`54.00`, listagem, consulta, todas as transições progressivas e os retornos
`400`, `404` e `422`. Os 53 testes existentes do backend também continuaram
passando.

Portanto, a implementação pode ser considerada concluída. A única ressalva é a
ausência da inspeção visual automatizada no navegador, que deve ser substituída
por uma validação visual manual final antes de uma entrega acadêmica ou
apresentação do sistema.
