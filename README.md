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

**Número de requisições necessárias**

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
- Licença
- Tópicos/tags

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
- **Reviews associados** (aninhado!)
- Estado do review (approved/changes_requested)
- Revisor

**5. Commits recentes (60 últimos)**

- Autor (nome, email, login)
- Data do commit


**6. Contribuidores (20 principais)**
- Login, nome
- Número de contribuições

### 2.6. Objetos Experimentais

50 repositórios mais populares do GitHub, selecionados por número 
de estrelas.

Critério de seleção:
- Repositórios públicos
- Mínimo de 50.000 estrelas
- Ordenados por stargazerCount (decrescente)

Cada repositório será submetido a ambos os tratamentos (REST e GraphQL) em design within-subjects.

### 2.7. Tipo de Projeto Experimental

**Design: Within-Subjects (Medidas Repetidas)**

Cada repositório é testado com AMBAS as APIs (GraphQL e REST), 
servindo como seu próprio controle. Isso elimina variabilidade 
entre repositórios e aumenta o poder estatístico do experimento.

**Estrutura:**
- Cada repositório → testado com REST (T1)
- Cada repositório → testado com GraphQL (T2)
- Ordem de execução: completamente randomizada
- Intervalo entre requisições: 1-2 segundos

**Combinações:**
- 50 repositórios × 2 tratamentos = 100 condições únicas
- Cada condição repetida 10 vezes
- Total: 1.000 medições

### 2.8. Quantidade de Medições

perguntar pro prof

### 2.9. Ameaças à Validade

#### Validade Interna:

1. **Rate limiting**: GitHub limita requisições (5.000/hora REST, 
pontos dinâmicos no GraphQL)
- **Mitigação**: Monitoramento ativo via endpoint `/rate_limit`, 
  pausas automáticas quando restantes < 200, distribuição temporal

2. **Cache**: Respostas podem estar em cache do GitHub
- **Mitigação**: Headers `Cache-Control: no-cache`, execução 
  distribuída no tempo, randomização da ordem

3. **Condições de rede**: Variações na latência e throughput
- **Mitigação**: 10 repetições por condição, execução em horários 
  variados, mesma máquina/rede para todas medições

4. **Efeitos de ordem**: Primeira execução pode ser diferente das 
subsequentes
- **Mitigação**: Randomização completa da ordem de execução dos 
  tratamentos

#### Validade Externa:

1. **Tamanho dos repositórios**: Apenas repositórios muito populares 
(>50k estrelas)
- **Mitigação**: Análise exploratória de correlação entre número 
  de estrelas e métricas. Documentar esta limitação explicitamente.

2. **Generalização para outras APIs**: Resultados específicos da 
implementação do GitHub
- **Mitigação**: Documentar características específicas das APIs 
  do GitHub. Resultados podem não generalizar para outras 
  implementações de GraphQL/REST.


#### Validade de Construção:

1. **Métricas incluem latência de rede**: Tempo medido inclui rede, 
não apenas processamento da API
- **Mitigação**: Usar mesma máquina/rede/horários para todas 
  medições. Tempo end-to-end é mais realista para desenvolvedores.


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
