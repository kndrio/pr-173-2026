# ADR-003: Estratégia de Microfrontends — Module Federation

**Status**: Aceito  
**Data**: 2026-03-28
**Autores**: Kennedy Carvalho

---

## Contexto

O desafio exige dois microfrontends (MFEs) independentes: um Shell (host de
autenticação e navegação) e um Orders MFE (CRUD de pedidos). A questão central
é **como compor dois MFEs de forma que sejam deployáveis e testáveis de forma
independente** sem duplicar código.

As opções consideradas:

1. **Composição via NGINX reverse proxy** — Shell em `:3000`, Orders MFE em `:3001`,
   o proxy encaminha `/pedidos/*` para o segundo container. Cada SPA tem seus próprios
   components, sem compartilhamento em runtime.

2. **Module Federation** (`@originjs/vite-plugin-federation`) — Shell como HOST
   carrega o remote `remoteEntry.js` do Orders MFE em runtime. Módulos `react`,
   `react-dom` e `react-router-dom` são `singleton`.

3. **Single-SPA** — Framework completo de orquestração de MFEs. Requer mudanças
   arquiteturais profundas em ambas as SPAs.

---

## Decisão

Adotar **Module Federation** via `@originjs/vite-plugin-federation`.

O ponto de inflexão foi identificado durante a implementação: a composição NGINX
resultaria em Shell e Orders MFE com **componentes idênticos duplicados**
(`OrderList`, `OrderForm`, `OrderDetail`, `StatusBadge`). Dois repositórios com
o mesmo código não são microfrontends — são uma duplicação.

**Arquitetura adotada:**
- `orders-mfe` expõe `./OrdersApp` como remote (`remoteEntry.js`)
- `shell` carrega `ordersApp/OrdersApp` via `React.lazy` + `Suspense`
- Token JWT passado via props: `<OrdersApp token={token} />`
- `react-router-dom` como singleton para evitar contexto dual de roteamento
- Navegação relativa em Orders MFE (`navigate('novo')`, não `/novo`) para
  funcionar tanto standalone (`:3001`) quanto federado (montado em `/pedidos/*`)


---

## Consequências

### Positivas

- **Sem duplicação**: Orders MFE é a fonte única de verdade para toda a lógica
  de pedidos. Shell consome o remote sem copiar código.
- **Deploy independente**: atualizar Orders MFE não requer rebuild do Shell —
  o Shell carrega o `remoteEntry.js` atualizado no próximo load.
- **Isolamento real**: cada MFE tem seu próprio `api.ts` com instâncias Axios
  independentes; falhas em um não afetam o outro diretamente.
- **Modo standalone preservado**: Orders MFE funciona em `:3001` sem o Shell
  para desenvolvimento e testes isolados.

### Negativas

- **Complexidade de CORS**: `remoteEntry.js` é carregado cross-origin; requer
  cabeçalho `Access-Control-Allow-Origin` no NGINX do Orders MFE.
  Detalhe: a location `/assets/remoteEntry.js` tem precedência de regex sobre
  prefixo — resolvido com `location /assets/` englobando todos os assets.
- **Build target obrigatório**: Vite requer `build.target: 'esnext'` e
  `minify: false` no remote para que o Module Federation funcione corretamente.
- **Token via props**: como cada MFE tem sua própria instância de módulo, o
  token não pode ser compartilhado via import de store — deve ser passado
  explicitamente via props. Simples, mas requer convenção explícita.
- **`tsconfig.node.json` incompatibilidade**: `composite: true` e `noEmit: true`
  são mutuamente exclusivos (TS6310); o `noEmit` deve ser removido do
  `tsconfig.node.json` de ambos os MFEs.
