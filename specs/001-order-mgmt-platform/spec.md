# Feature Specification: Order Management Platform MVP

**Feature Branch**: `001-order-mgmt-platform`
**Created**: 2026-03-30
**Status**: Draft
**Input**: Plataforma interna de gestão de pedidos para e-commerce — substituindo controle por planilhas por sistema centralizado com autenticação, serviço de pedidos e frontend modular.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Operador Autentica e Acessa a Plataforma (Priority: P1)

Um operador novo ou existente precisa criar conta e acessar a plataforma de forma segura para começar a gerenciar pedidos.

**Why this priority**: Sem autenticação funcional, nenhuma outra funcionalidade pode ser acessada. É o pré-requisito de todo o sistema.

**Independent Test**: Pode ser testado de forma isolada acessando o fluxo de registro/login sem qualquer pedido existente. Entrega valor imediato ao demonstrar que o sistema está acessível e seguro.

**Acceptance Scenarios**:

1. **Given** um visitante sem conta, **When** ele preenche nome completo, email válido e senha com mínimo de 8 caracteres e submete o formulário de registro, **Then** a conta é criada, o usuário é autenticado automaticamente e redirecionado para a tela principal.
2. **Given** um usuário com conta existente, **When** ele informa email e senha corretos na tela de login, **Then** recebe acesso à plataforma com uma sessão autenticada.
3. **Given** um usuário autenticado, **When** ele acessa a área de perfil, **Then** visualiza seus dados pessoais (nome, email, papel).
4. **Given** alguém tentando registrar com email já existente, **When** submete o formulário, **Then** recebe mensagem de erro clara informando que o email já está em uso.
5. **Given** alguém tentando registrar com senha menor que 8 caracteres, **When** submete o formulário, **Then** recebe validação indicando o requisito mínimo de senha.

---

### User Story 2 - Operador Cria um Novo Pedido (Priority: P1)

Um operador precisa registrar um pedido recebido de um cliente, incluindo todos os itens e informações relevantes, para que o pedido entre no fluxo de trabalho.

**Why this priority**: A criação de pedidos é a ação central da plataforma. Sem ela, o sistema não gera valor operacional.

**Independent Test**: Pode ser testado criando um pedido com itens e verificando que o valor total foi calculado corretamente e o pedido aparece na listagem. Entrega o valor central do MVP.

**Acceptance Scenarios**:

1. **Given** um operador autenticado no formulário de criação, **When** ele preenche nome do cliente, email, descrição, adiciona ao menos um item (nome, quantidade, preço unitário), seleciona prioridade e submete, **Then** o pedido é criado com status "pendente" e o valor total é calculado automaticamente como soma de (quantidade × preço) de cada item.
2. **Given** um operador no formulário de criação, **When** ele adiciona múltiplos itens dinamicamente, **Then** o formulário exibe todos os itens adicionados e o total é atualizado em tempo real.
3. **Given** um operador no formulário de criação, **When** ele remove um item da lista, **Then** o item é removido e o total é recalculado.
4. **Given** um operador que submeteu o formulário sem preencher campos obrigatórios, **When** tenta criar o pedido, **Then** recebe validações indicando quais campos são necessários.
5. **Given** um pedido recém-criado, **When** o operador acessa o detalhe do pedido, **Then** visualiza todos os dados incluindo itens, total e status atual.

---

### User Story 3 - Operador Gerencia Status de Pedidos (Priority: P2)

Um operador precisa atualizar o status dos pedidos conforme o trabalho avança, garantindo que apenas transições válidas sejam permitidas.

**Why this priority**: O ciclo de vida dos pedidos é essencial para a operação. Sem controle de status, não há visibilidade do fluxo de trabalho.

**Independent Test**: Pode ser testado com pedidos já criados, verificando que as transições válidas são permitidas e as inválidas são bloqueadas.

**Acceptance Scenarios**:

1. **Given** um pedido com status "pendente", **When** o operador clica em "Iniciar Atendimento", **Then** o status é atualizado para "em andamento".
2. **Given** um pedido com status "em andamento", **When** o operador clica em "Concluir", **Then** o status é atualizado para "concluído".
3. **Given** um pedido em qualquer status (exceto "cancelado" e "concluído"), **When** o operador clica em "Cancelar", **Then** o status é atualizado para "cancelado".
4. **Given** um pedido com status "concluído", **When** o operador tenta reverter para "em andamento", **Then** a ação é bloqueada e nenhuma mudança ocorre.
5. **Given** um pedido com status "pendente", **When** o operador tenta alterar para "concluído" diretamente, **Then** a ação é bloqueada — apenas transições sequenciais válidas são aceitas.

---

### User Story 4 - Operador Consulta e Filtra Pedidos (Priority: P2)

Um operador precisa encontrar rapidamente pedidos específicos usando filtros e paginação para gerenciar o volume de trabalho diário.

**Why this priority**: Sem capacidade de busca e filtragem, a listagem de pedidos torna-se inutilizável com volume real de dados.

**Independent Test**: Pode ser testado com dados de seed, verificando que filtros e paginação funcionam corretamente de forma independente da criação de novos pedidos.

**Acceptance Scenarios**:

1. **Given** uma lista com múltiplos pedidos de status variados, **When** o operador filtra por status "pendente", **Then** apenas pedidos pendentes são exibidos com o contador atualizado.
2. **Given** uma lista com pedidos de prioridades diferentes, **When** o operador filtra por prioridade "urgente", **Then** apenas pedidos urgentes são exibidos.
3. **Given** uma lista com mais pedidos do que o limite por página, **When** o operador navega para a próxima página, **Then** a próxima leva de pedidos é exibida.
4. **Given** a listagem de pedidos, **When** carregada, **Then** pedidos são exibidos em ordem decrescente de data de criação por padrão.
5. **Given** um sistema sem pedidos ou filtro sem resultados, **When** a listagem é exibida, **Then** um estado vazio informativo é mostrado.

---

### User Story 5 - Operador Usa Análise de IA para Priorização (Priority: P3)

Um operador com dúvida sobre a prioridade de um pedido pode solicitar uma análise automatizada para obter sugestão de prioridade e um resumo executivo do pedido.

**Why this priority**: Funcionalidade de valor agregado que acelera a tomada de decisão, mas não é bloqueante para a operação básica.

**Independent Test**: Pode ser testado em um pedido existente, clicando em "Analisar com IA" e verificando que um resultado é retornado (seja da análise inteligente ou via regras de fallback).

**Acceptance Scenarios**:

1. **Given** um pedido aberto, **When** o operador clica em "Analisar com IA", **Then** um indicador de carregamento é exibido enquanto a análise é processada.
2. **Given** a análise concluída com sucesso, **When** o resultado é retornado, **Then** o operador visualiza a prioridade sugerida e um resumo executivo do pedido.
3. **Given** que o serviço de análise inteligente está indisponível, **When** o operador solicita análise, **Then** o sistema retorna uma sugestão baseada em regras automáticas, sem apresentar erro técnico ao usuário.
4. **Given** o resultado da análise exibido, **When** o operador discorda da sugestão, **Then** pode ignorar a recomendação e manter/alterar a prioridade manualmente.

---

### User Story 6 - Administrador Visualiza Usuários da Plataforma (Priority: P3)

Um administrador precisa visualizar os usuários cadastrados na plataforma para monitorar o acesso e apoiar a gestão de equipe.

**Why this priority**: Funcionalidade de suporte operacional necessária mas não crítica para o fluxo principal de pedidos.

**Independent Test**: Pode ser testado acessando a listagem de usuários com dados de seed, verificando paginação e dados exibidos.

**Acceptance Scenarios**:

1. **Given** um administrador autenticado, **When** acessa a listagem de usuários, **Then** visualiza todos os usuários ativos com paginação.
2. **Given** a listagem de usuários, **When** exibida, **Then** mostra nome, email e papel de cada usuário.

---

### Edge Cases

- O que acontece quando um pedido é criado sem nenhum item na lista?
- Como o sistema se comporta quando a lista de pedidos está vazia (primeiro acesso, sem dados criados)?
- O que ocorre se a sessão do usuário expirar durante a navegação — o sistema redireciona para login automaticamente?
- Como é tratada uma tentativa de acesso direto a um pedido que não existe (identificador inválido)?
- O que acontece se o cálculo de total resultar em zero (itens com quantidade ou preço zero)?
- Como o sistema reage a múltiplos cliques simultâneos no botão de análise de IA (evitar requisições duplicadas)?
- O que acontece ao tentar criar um pedido com email de cliente em formato inválido?

---

## Requirements *(mandatory)*

### Functional Requirements

**Autenticação e Usuários:**

- **FR-001**: O sistema DEVE permitir o registro de novos usuários com nome completo, endereço de email e senha.
- **FR-002**: O sistema DEVE validar que o email informado no registro é único — dois usuários não podem compartilhar o mesmo endereço de email.
- **FR-003**: O sistema DEVE exigir senha com mínimo de 8 caracteres no registro.
- **FR-004**: O sistema DEVE armazenar senhas de forma segura, nunca em texto legível.
- **FR-005**: O sistema DEVE autenticar usuários via email e senha, retornando uma credencial de sessão válida.
- **FR-006**: O sistema DEVE disponibilizar um endpoint para que o usuário autenticado consulte seus próprios dados de perfil.
- **FR-007**: O sistema DEVE permitir listagem de usuários ativos com suporte a paginação.
- **FR-008**: A credencial de sessão DEVE ser mantida em memória no cliente, não em armazenamento persistente do navegador (localStorage/cookies persistentes).

**Pedidos:**

- **FR-009**: O sistema DEVE permitir a criação de pedidos contendo: nome do cliente, email do cliente, descrição, lista de itens (nome, quantidade, preço unitário), nível de prioridade e observações opcionais.
- **FR-010**: O sistema DEVE calcular automaticamente o valor total do pedido como soma de (quantidade × preço unitário) de cada item.
- **FR-011**: Pedidos recém-criados DEVEM ter status inicial "pendente".
- **FR-012**: O sistema DEVE suportar quatro níveis de prioridade: baixa, média, alta e urgente.
- **FR-013**: O sistema DEVE permitir listagem de pedidos com paginação, filtro combinável por status e por prioridade, e ordenação por data de criação.
- **FR-014**: O sistema DEVE permitir consulta de um pedido específico por identificador, retornando todos os seus dados incluindo a lista completa de itens.
- **FR-015**: O sistema DEVE permitir atualização de status respeitando as seguintes transições válidas: pendente → em_andamento; em_andamento → concluido; pendente → cancelado; em_andamento → cancelado. Pedidos com status `concluido` ou `cancelado` são **estados finais imutáveis** — nenhuma transição é permitida a partir deles.
- **FR-016**: O sistema DEVE rejeitar transições de status inválidas, retornando mensagem de erro descritiva.
- **FR-017**: O sistema DEVE manter listagens em cache para otimizar o desempenho, invalidando automaticamente o cache quando pedidos são criados ou atualizados.
- **FR-018**: O sistema DEVE emitir notificações de eventos quando pedidos são criados (order_created) ou atualizados (order_updated), permitindo integração com outros sistemas.
- **FR-019**: O sistema DEVE disponibilizar um endpoint de análise de pedido que retorna sugestão de prioridade e resumo executivo em linguagem natural.
- **FR-020**: O endpoint de análise DEVE funcionar mesmo quando o serviço externo de análise inteligente estiver indisponível, aplicando regras automáticas como fallback sem expor o erro ao usuário.

**Frontend — Shell/Host:**

- **FR-021**: A interface DEVE apresentar layout responsivo com cabeçalho, navegação lateral e área de conteúdo principal.
- **FR-022**: A interface DEVE oferecer fluxo completo de login e registro acessível sem autenticação prévia.
- **FR-023**: A credencial de sessão DEVE ser compartilhada entre todos os módulos da interface sem necessidade de reautenticação ao navegar.
- **FR-024**: A interface DEVE suportar roteamento entre as diferentes páginas da aplicação.

**Frontend — Módulo de Pedidos:**

- **FR-025**: A interface DEVE exibir pedidos em lista ou tabela com indicadores visuais de status (badges coloridos).
- **FR-026**: A interface DEVE disponibilizar filtros por status e prioridade com contadores indicando a quantidade de pedidos em cada categoria.
- **FR-027**: A interface DEVE permitir adição e remoção dinâmica de itens no formulário de criação de pedido.
- **FR-028**: A interface DEVE exibir a página de detalhe de um pedido com todos os seus dados.
- **FR-029**: A interface DEVE exibir apenas os botões de transição de status válidos para o estado atual do pedido.
- **FR-030**: A interface DEVE incluir um botão "Analisar com IA" na página de detalhe do pedido, exibindo o resultado da análise após o retorno.
- **FR-031**: A interface DEVE exibir estados de carregamento durante operações assíncronas.
- **FR-032**: A interface DEVE exibir estados vazios informativos quando não há dados a mostrar.
- **FR-033**: A interface DEVE apresentar mensagens de erro amigáveis em caso de falhas, sem expor detalhes técnicos ao usuário.

**Operacional e Qualidade:**

- **FR-034**: Toda a stack de serviços DEVE poder ser iniciada com um único comando de orquestração de containers.
- **FR-035**: Cada serviço de backend DEVE disponibilizar documentação interativa de sua API acessível via navegador em uma rota dedicada.
- **FR-036**: O sistema DEVE incluir dados de demonstração realistas pré-carregados para permitir avaliação sem necessidade de criação manual de registros.
- **FR-037**: O repositório DEVE incluir documentação com diagrama de arquitetura e registro das decisões técnicas relevantes.
- **FR-038**: O sistema DEVE executar testes automatizados dos endpoints principais a cada alteração de código via pipeline de integração contínua.

### Key Entities

- **Usuário**: Representa uma pessoa com acesso à plataforma. Possui nome completo, email (único), senha (protegida), papel (operador/gestor/administrador) e status ativo/inativo.
- **Pedido**: Representa uma solicitação registrada. Possui identificador único, dados do cliente (nome, email), descrição, lista de itens, valor total calculado, prioridade, status (pendente/em_andamento/concluido/cancelado), observações, data de criação e data de última atualização.
- **Item de Pedido**: Componente de um pedido representando um produto ou serviço. Possui nome, quantidade e preço unitário. O subtotal (quantidade × preço) é calculado e armazenado no momento da criação do pedido para eficiência de consulta.
- **Evento de Pedido**: Notificação emitida para sistemas externos quando o estado de um pedido muda. Contém tipo de evento, identificador do pedido afetado e timestamp do evento.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operadores conseguem registrar um novo pedido completo (com múltiplos itens) em menos de 3 minutos.
- **SC-002**: A listagem de pedidos carrega e exibe resultados em menos de 2 segundos para volumes de até 10.000 pedidos.
- **SC-003**: O resultado da análise (inteligente ou por regras de fallback) é retornado em menos de 10 segundos após a solicitação.
- **SC-004**: 100% das tentativas de transição de status inválida são bloqueadas pelo sistema, sem degradação de dados.
- **SC-005**: A plataforma completa fica disponível para uso em menos de 5 minutos a partir do único comando de inicialização.
- **SC-006**: 95% dos fluxos principais (login, criação de pedido, atualização de status) são completados com sucesso por novos usuários na primeira tentativa.
- **SC-007**: Todos os testes automatizados são executados e reportam resultado (passou/falhou) em menos de 5 minutos no pipeline de integração contínua.
- **SC-008**: O valor total de um pedido reflete corretamente a soma dos itens em 100% dos casos, sem discrepância.
- **SC-009**: O sistema mantém disponibilidade durante operações de criação e atualização de pedidos sem perda de dados.

---

## Assumptions

- Os três papéis de usuário (Operador, Gestor, Administrador) compartilham o mesmo fluxo de autenticação; diferenças de permissão são simples e não requerem sistema de autorização granular no MVP.
- Gestores não precisam de dashboard com gráficos no MVP — a visualização da listagem com filtros e contadores atende ao requisito de monitoramento básico.
- O fluxo de recuperação de senha não faz parte do escopo do MVP; usuários com senha esquecida devem contatar o administrador.
- Não há requisito de notificação por email para eventos de pedido no MVP — as notificações via eventos são para integração interna entre serviços.
- O sistema operará em ambiente controlado (intranet corporativa) e não precisa suportar autenticação via redes sociais ou SSO corporativo no MVP.
- Não há requisito de internacionalização no MVP — a plataforma será inteiramente em português brasileiro.
- O módulo de análise é um auxiliar de decisão, não um sistema de automação — o operador sempre tem a palavra final sobre a prioridade do pedido.
- Dados de seed serão suficientes para demonstração; não há requisito de migração de dados das planilhas existentes no MVP.
- Todos os valores monetários são em Real brasileiro (BRL), sem necessidade de conversão de moeda ou formatação multi-moeda.
- A interface modular (microfrontends) não precisa suportar carregamento independente de cada módulo em produção no MVP — a orquestração local via docker-compose é suficiente.
