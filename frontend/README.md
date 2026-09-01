# Front-end — Pedidos da Lanchonete

Interface de uso interno para registrar pedidos de mesas, consultar pedidos e
acompanhar o trabalho da cozinha. O projeto usa React 19, TypeScript, Vite,
CSS puro e `fetch` nativo.

## Requisitos

- Node.js 20.19 ou superior (desenvolvido e validado com Node.js 24.19.0)
- npm
- Backend FastAPI deste repositório ativo em `http://127.0.0.1:8000`

## Instalação e execução

Na pasta `frontend/`:

```bash
npm install
npm run dev
```

O Vite informa o endereço local da aplicação. Durante o desenvolvimento, o
proxy configurado em `vite.config.ts` encaminha requisições relativas iniciadas
por `/api` para `http://127.0.0.1:8000`; por isso o backend deve permanecer
ativo enquanto a interface é usada.

A variável opcional `VITE_API_BASE_URL` permite alterar o prefixo da API. O
valor local padrão é `/api`, conforme documentado em `.env.example`.

## Verificação

```bash
npm run lint
npm run build
```

## Estrutura principal

- `src/types/api.ts`: tipos espelhados do OpenAPI.
- `src/api/pedidosApi.ts`: cliente HTTP e normalização de erros.
- `src/components/FormularioPedido.tsx`: criação e total estimado.
- `src/components/ConsultaPedido.tsx`: consulta real pelo ID.
- `src/components/CartaoPedido.tsx`: dados e ações de cada pedido.
- `src/components/ListaPedidos.tsx`: estados da listagem.
- `src/App.tsx`: carregamento inicial e coordenação do estado compartilhado.
- `src/App.css` e `src/index.css`: estilos responsivos e acessíveis.

Os pedidos são mantidos somente na memória do backend. Reiniciar a API limpa a
lista e reinicia a sequência de IDs.
