# ADR-001: Spec-Driven Development com SpecKit

**Status**: Aceito  
**Data**: 2026-03-27  
**Autores**: Kennedy Carvalho

---

## Contexto

O desafio técnico impõe restrições claras: tempo compartilhado, aproximadamente 7 dias,
entrega de um PMV com dois microserviços, dois microfrontends, banco de
dados, cache, CI e bônus compostos por integração com IA, observabilidade, comunicação 
assíncrona entre microserviços via fila, documentação da API.

Nesse contexto, o maior risco não seria apenas a velocidade de codificação, mas tomar decisões
arquiteturais erradas cedo e pagar o custo do retrabalho depois. Sem um processo
estruturado, até mesmo o uso de IA pode gerar código incoerente, inseguro ou mesmo 
inconsistente com a visão geral do sistema e seus requisitos.

A questão central: **como manter governança técnica em desenvolvimento
acelerado por IA, sem criar overhead de processo?**

---

## Decisão

Adotar **Spec-Driven Development (SDD)** via
[SpecKit](https://github.com/github/spec-kit) como metodologia principal.

O processo seguido:

1. **Constitution** — 10 princípios inegociáveis definidos antes de qualquer código
2. **Specification** — user stories com critérios de aceite verificáveis
3. **Plan** — decisões técnicas, trade-offs e estrutura de arquivos
4. **Tasks** — 90+ tarefas faseadas com critérios de aceite individuais
5. **Implement** — código gerado e revisado a partir das specs

Todos os artefatos versionados em `.specify/` e `specs/`, tornando cada decisão
rastreável da spec ao commit.

**Referências que informaram a adoção:**
- GitHub Spec Kit — adotado por IBM e EPAM para desenvolvimento assistido por IA
- Padrão de "specification by example" (BDD) como base para critérios de aceite
- Experiência própria com retrabalho em projetos sem specs formalizadas

---

## Consequências

### Positivas

- **Rastreabilidade**: qualquer linha de código é explicável por uma task, que
  deriva de uma user story, que deriva de um princípio da constituição.
- **Multiplicação de capacidade**: o modelo de IA opera com contexto completo —
  não precisa inferir intenção porque a intenção está documentada.
- **Onboarding imediato**: um avaliador pode entender o projeto lendo
  `spec.md` e `plan.md` antes de abrir qualquer arquivo de código.
- **Governança sem overhead**: as specs substituem reuniões de alinhamento;
  o processo é assíncrono por natureza.
- **Disciplina forçada**: a regra "spec → código, nunca código → spec retroativa"
  previne racionalização post-hoc de decisões ruins.

### Negativas

- **Investimento inicial**: escrever constitution + spec + plan consome ~4-6h
  antes do primeiro commit de código.
- **Risco de over-spec**: specs muito detalhadas podem engessar a implementação
  quando a realidade técnica diverge do planejado.
- **Custo de manutenção**: specs desatualizadas são piores que ausência de specs —
  requerem disciplina contínua de atualização.

### Mitigações aplicadas

O processo foi calibrado para PMV: specs suficientes para governança, não
documentação exaustiva. Tarefas com critério "funciona e passa nos testes" são
preferidas a tarefas com critério "implementa todos os edge cases".
