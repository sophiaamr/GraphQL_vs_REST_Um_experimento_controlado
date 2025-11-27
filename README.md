# 📝 Relatório Técnico de Laboratório

## 1. Informações do grupo
- **Curso:** Engenharia de Software
- **Disciplina:** Laboratório de Experimentação de Software
- **Período:** 6° Período
- **Professor(a):** Prof. Wesley Dias Maciel
- **Membros do Grupo:** Sophia Mendes, Thiago Andrade

---

## 2. Introdução

As APIs (Application Programming Interfaces) são fundamentais para a comunicação entre sistemas distribuídos na Web. O estilo arquitetural REST (Representational State Transfer) tem sido o paradigma dominante por décadas, mas novas abordagens têm surgido para atender às demandas de aplicações mais complexas.

O GraphQL, desenvolvido pelo Facebook em 2012, representa uma dessas alternativas. Diferentemente do REST, que utiliza múltiplos endpoints fixos, o GraphQL oferece um único endpoint onde os clientes especificam exatamente quais dados necessitam, prometendo maior flexibilidade e eficiência.

### 2.1. Questões de Pesquisa (Research Questions – RQs)
**Questões de Pesquisa - Research Questions (RQs):**

| RQ   | Pergunta |
|------|----------|
| RQ01 | Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST? |
| RQ02 | Respostas às consultas GraphQL tem tamanho menor que respostas às consultas REST? |

### 2.2. Hipóteses 

Para RQ1

H0: Não há diferença significativa no tempo de resposta entre consultas GraphQL e REST

H1: Consultas GraphQL apresentam tempo de resposta significativamente menor que REST

Para RQ2:

H0: Não há diferença significativa no tamanho das respostas entre GraphQL e REST

H1: Respostas GraphQL apresentam tamanho significativamente menor que REST

### 2.3. Variáveis dependentes

**Tempo de Resposta (ms)**: Tempo decorrido desde o envio da requisição até o recebimento completo da resposta

**Tamanho da Resposta (bytes)**: Tamanho do payload da resposta em bytes

**Número de requisições necessárias**: Quantidade de chamadas HTTP realizadas

**Métricas de Rate Limit**:
- Rate limit antes da requisição
- Rate limit após a requisição
- Rate limit consumido
- Custo da query (GraphQL)
- Timestamp de reset do rate limit

### 2.4. Variáveis independentes

**Tipo de API**: REST ou GraphQL


### 2.5. Tratamentos

T1: Requisições usando API REST

T2: Requisições usando API GraphQL


Ambos os tratamentos coletam o mesmo conjunto de informações:

**1. Dados básicos do repositório**
- Nome, descrição, URL
- Contadores: estrelas, forks, watchers, open issues
- Datas: criação, última atualização
- Linguagem principal

**2. Linguagens utilizadas no repositório**
- Lista completa de linguagens com percentuais

**3. Issues abertas (60 mais recentes)**
- Título, número, estado
- Data de criação
- Autor (login)
- Labels associadas

**4. Pull Requests abertos (60 mais recentes)**
- Título, número, estado
- Data de criação
- Autor (login)
- Status de merge
- **Reviews associados (apenas dos 10 primeiros PRs)**
  - Limitação aplicada em ambas APIs para viabilidade de rate limit
  - Até 10 reviews por PR
- Estado do review (approved/changes_requested)
- Revisor

**5. Commits recentes (60 últimos)**

- Autor (nome, email, login)


**6. Contribuidores (20 principais)**
- Login, nome

## 2.6. Objetos Experimentais

**100 repositórios mais populares do GitHub**, selecionados dinamicamente via API.

**Critério de seleção:**
- Repositórios públicos  
- Mínimo de 50.000 estrelas  
- Ordenados por `stargazerCount` (decrescente)  
- Buscados dinamicamente via GitHub Search API
- Cada repositório será submetido a **ambos os tratamentos** (REST e GraphQL) em design *within-subjects*.

### Estrutura de Execução Incremental

O experimento será executado em **5 fases progressivas** para permitir análise granular do comportamento das APIs em diferentes escalas:

| Fase | Repositórios | Objetivo |
|------|--------------|----------|
| Fase 1 | 60 | Baseline inicial |
| Fase 2 | 70 | Incremento de 10 repos |
| Fase 3 | 80 | Incremento de 10 repos |
| Fase 4 | 90 | Incremento de 10 repos |
| Fase 5 | 100 | Dataset completo |

### Justificativa da abordagem incremental
- Identificar pontos de inflexão no desempenho   
- Detectar degradação progressiva em tempo ou tamanho  
- Permitir análise comparativa entre APIs em diferentes volumes  

---

## 2.7. Tipo de Projeto Experimental

### Design: *Within-Subjects* (Medidas Repetidas) com Progressão Incremental

Cada repositório é testado com **AMBAS** as APIs (GraphQL e REST)

### Estrutura
- Cada repositório → REST (T1)  
- Cada repositório → GraphQL (T2)  
- Ordem **completamente randomizada** dentro de cada fase  
- Intervalo entre requisições: **1–2 segundos**  
- Intervalo entre fases: análise preliminar  


---

## 2.8. Quantidade de Medições

### Estrutura de Medições
Cada repositório será testado **1 vez** com cada API (REST e GraphQL)

## Medições por Fase

| Fase | Repositórios | Cálculo        | Medições       |
|------|--------------|----------------|----------------|
| Fase 1 | 60  | 60 × 2  | **120 medições** |
| Fase 2 | 70  | 70 × 2  | **140 medições** |
| Fase 3 | 80  | 80 × 2 | **160 medições** |
| Fase 4 | 90  | 90 × 2 | **180 medições** |
| Fase 5 | 100 | 100 × 2 | **200 medições** |

### **Total acumulado: 800 medições**


---

## 2.9. Ameaças à Validade

### **Validade Interna**

#### Rate limiting progressivo
**Problema:** 800 medições podem ultrapassar limites do GitHub.  
**Mitigação:**  
- Captura automática de rate limit antes/depois de cada requisição
- Registro de consumo de rate limit no CSV
- Pausa automática quando rate limit < 200
- Reviews limitados a 10 PRs no REST
- Análise incremental para detectar impacto

#### Efeito de aprendizado entre fases
**Problema:** Cache/otimizações do GitHub podem alterar resultados entre fases.  
**Mitigação:**  
- Reexecutar todos os repositórios de cada fase  
- `Cache-Control: no-cache`  
- Randomização total  

#### Condições de rede variáveis
**Problema:** Mudanças na rede entre fases.  
**Mitigação:**  
- Mesma máquina e conexão  
- Registro de timestamps  
- Modelagem com fase como covariável  

#### Fadiga do sistema
**Problema:** Degradação local de recursos.  
**Mitigação:**  
- Reiniciar script entre fases  
- Monitoramento CPU/memória  

---

### **Validade Externa**

#### Tamanho e popularidade dos repositórios
**Problema:** Apenas repositórios com >50k estrelas.  
**Mitigação:**  
- Amostra de 100 aumenta diversidade  
- Análise de correlação com tamanho/estrelas  


---

### **Validade de Construção**

#### Latência de rede
**Mitigação:**
- Mesma rede = condições equivalentes 


---

## 3. Metodologia


---

## 4. Dificuldades


---

### 5 Métricas

---

## 6. Resultados & Discussões

---

## 7. Conclusão
 

---
