# Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning

> Texto da proposta de iniciação científica. Por exigência do modelo de submissão, o
> documento não traz os nomes dos autores nem do curso. Tamanho exigido: de 2 a 10 páginas.

## Resumo

Este projeto propõe investigar a aplicação de teoria dos grafos e métodos de machine
learning para detecção de fraudes em transações PIX no contexto brasileiro. A pesquisa
busca modelar transações financeiras como grafos, nos quais contas representam vértices e
transferências representam arestas, permitindo a análise estrutural de comportamentos
suspeitos. A motivação do estudo está relacionada ao crescimento de fraudes digitais
associadas ao PIX e à necessidade de métodos mais inteligentes, interpretáveis e
cientificamente fundamentados para identificação de padrões anômalos. Como parte do
projeto, pretende-se desenvolver um dataset sintético de transações PIX fundamentado em
análise exploratória de dados e em cenários inspirados em fraudes reais, como contas
laranja, intermediários e lavagem em cadeia, ou, se possível, utilizar dados públicos
disponibilizados pelo Banco Central do Brasil para complementar a pesquisa. Técnicas como
Isolation Forest e DBSCAN serão utilizadas para análise de anomalias, além da aplicação de
visualizações baseadas em grafos e heatmaps de risco ("grafos de calor"), buscando
aumentar a interpretabilidade dos resultados. Espera-se contribuir cientificamente para as
áreas de Inteligência Artificial, Ciência de Dados, Segurança Financeira e Análise de
Redes Complexas.

## Introdução

A crescente digitalização dos serviços financeiros no Brasil, impulsionada principalmente
pela popularização do sistema PIX desenvolvido pelo Banco Central do Brasil, ampliou
significativamente o volume e a velocidade das transações eletrônicas. Apesar dos avanços
em praticidade e inclusão financeira, esse cenário também favoreceu o crescimento de
fraudes digitais, como contas laranja, golpes de falso suporte bancário, clonagem de
WhatsApp e esquemas de lavagem de dinheiro em cadeia. Nesse contexto, torna-se necessário
investigar métodos computacionais capazes de identificar padrões anômalos de forma
automatizada, interpretável e escalável.

Entre os principais conceitos utilizados no projeto estão teoria dos grafos, detecção de
anomalias e *machine learning*. A teoria dos grafos permite representar sistemas
financeiros como redes complexas, nas quais contas bancárias são modeladas como vértices e
transações como arestas. Essa abordagem possibilita analisar relações estruturais entre
usuários, identificar padrões de conectividade e detectar comportamentos suspeitos que
frequentemente não são perceptíveis em modelos tabulares tradicionais. Métricas como grau,
centralidade e intermediação (*betweenness centrality*) vêm sendo amplamente exploradas em
pesquisas relacionadas à análise de redes financeiras e segurança cibernética.

Na área de Inteligência Artificial, técnicas de detecção de anomalias têm sido utilizadas
para identificar padrões incomuns em grandes volumes de dados. Métodos como Isolation
Forest e DBSCAN destacam-se por sua aplicação em cenários com poucos dados rotulados,
característica comum em problemas de fraude financeira. O estado da arte em pesquisa
aponta um crescimento significativo de abordagens híbridas, combinando aprendizado de
máquina com análise estrutural de grafos, permitindo não apenas detectar fraudes, mas
compreender como elas se propagam dentro das redes financeiras.

No contexto de mercado e sociedade, instituições financeiras e empresas de tecnologia vêm
investindo em sistemas inteligentes de monitoramento transacional para reduzir perdas
financeiras e aumentar a segurança digital. Entretanto, muitos modelos utilizados
atualmente ainda apresentam baixa interpretabilidade, dificultando compreender por que
determinadas transações são classificadas como suspeitas. Além disso, parte das soluções
comerciais depende de dados proprietários, o que limita a reprodutibilidade científica e o
desenvolvimento acadêmico de novas abordagens.

Diante desse cenário, este projeto pretende pesquisar como a combinação entre teoria dos
grafos, técnicas de detecção de anomalias e visualizações baseadas em heatmaps de risco
("grafos de calor") pode contribuir para identificação e interpretação de fraudes em
transações PIX, utilizando um dataset sintético fundamentado em análise exploratória de
dados ou, se possível, dados públicos disponibilizados pelo Banco Central do Brasil.

## 1. Objetivos do Projeto

### Objetivo Geral

Investigar a aplicação conjunta de teoria dos grafos e métodos de machine learning para
detecção e análise de fraudes em transações PIX no contexto brasileiro, buscando
identificar padrões anômalos e aumentar a interpretabilidade dos resultados por meio de
representações em grafos, visualizações tradicionais de redes e heatmaps de risco.

### Objetivos Específicos

1. Pesquisar conceitos relacionados à teoria dos grafos, detecção de anomalias e fraudes
   financeiras digitais aplicadas ao sistema PIX.
2. Desenvolver ou, se possível, utilizar um dataset de transações PIX fundamentado em
   análise exploratória de dados e em padrões inspirados em fraudes reais.
3. Modelar as transações financeiras como grafos, representando contas bancárias como
   vértices e transferências financeiras como arestas.
4. Aplicar conceitos estudados em aula na disciplina de Teoria dos Grafos para
   construção, interpretação e visualização de redes financeiras.
5. Extrair métricas estruturais dos grafos, como grau, centralidade e intermediação
   (*betweenness centrality*), para caracterização de comportamentos financeiros.
6. Aplicar técnicas de detecção de anomalias, como Isolation Forest e DBSCAN, para
   identificação de padrões suspeitos.
7. Analisar diferentes perfis de fraude, como contas laranja, intermediários, coletores e
   estruturas de lavagem de dinheiro em cadeia.
8. Comparar abordagens baseadas em dados tabulares com abordagens fundamentadas em teoria
   dos grafos.
9. Desenvolver visualizações baseadas em grafos tradicionais e heatmaps de risco ("grafos
   de calor"), visando melhorar a interpretabilidade e identificação de "vértices quentes".
10. Avaliar a eficácia das técnicas aplicadas por meio de métricas de desempenho e análise
    dos resultados obtidos.
11. Contribuir para pesquisas nas áreas de Inteligência Artificial, Ciência de Dados,
    Segurança Financeira e Análise de Redes Complexas.

## 2. Procedimentos Metodológicos

A pesquisa será conduzida por meio de uma abordagem quantitativa e aplicada, utilizando
conceitos de teoria dos grafos, análise exploratória de dados e técnicas de machine
learning voltadas à detecção de anomalias em transações financeiras.

Inicialmente, será realizada uma revisão bibliográfica sobre fraudes digitais no sistema
PIX, análise de redes complexas e métodos computacionais utilizados na identificação de
comportamentos suspeitos em sistemas financeiros, buscando compreender o estado da arte
das soluções acadêmicas e práticas relacionadas ao tema.

Na etapa experimental, pretende-se desenvolver um dataset sintético de transações PIX
fundamentado em padrões estatísticos e cenários inspirados em fraudes reais, como contas
laranja, intermediários, golpes de falso suporte bancário, clonagem de WhatsApp e lavagem
de dinheiro em cadeia. Caso seja viável, também poderão ser utilizados dados públicos
disponibilizados pelo Banco Central do Brasil para complementar a análise e aumentar o
realismo da simulação.

As transações serão modeladas como grafos, nos quais os vértices representarão contas
bancárias e as arestas representarão transferências financeiras. A partir dessa
estrutura, pretende-se aplicar conceitos estudados na disciplina de Teoria dos Grafos,
buscando compreender como métricas estruturais podem auxiliar na identificação de padrões
suspeitos em redes financeiras. Serão utilizadas visualizações tradicionais de grafos para
interpretação das conexões entre contas, além de representações baseadas em heatmaps de
risco ("grafos de calor"), permitindo identificar vértices com maior probabilidade de
comportamento anômalo.

Posteriormente, serão extraídas métricas de redes complexas, como grau, centralidade e
intermediação (*betweenness centrality*), utilizadas como variáveis de entrada para
algoritmos de detecção de anomalias. Para análise dos dados, serão aplicadas técnicas de
machine learning, como Isolation Forest e DBSCAN, escolhidas por sua capacidade de
identificar padrões incomuns em conjuntos de dados com baixa rotulação de fraude, cenário
comum em problemas financeiros reais.

Os resultados serão avaliados por meio de métricas quantitativas de desempenho e
comparações entre abordagens baseadas em dados tabulares e representações em grafos. Essa
abordagem é adequada ao problema proposto porque fraudes financeiras geralmente
apresentam padrões relacionais e comportamentais difíceis de serem observados em análises
tradicionais exclusivamente tabulares, tornando a modelagem em grafos uma alternativa
relevante para ampliar a interpretabilidade e compreensão das redes de fraude.

O projeto não envolverá coleta de dados pessoais reais, experimentação com seres humanos
ou utilização de animais. Caso sejam utilizados dados públicos, serão respeitadas as
diretrizes de privacidade e anonimização previstas pela legislação vigente, incluindo
princípios relacionados à LGPD (Lei Geral de Proteção de Dados).

## 3. Cronograma

Ver [cronograma.md](cronograma.md).

## 4. Referências Bibliográficas

Algumas referências bibliográficas, cursos e materiais complementares poderão ser
consultados e adicionados ao longo do desenvolvimento da iniciação científica, conforme a
evolução da pesquisa, aprofundamento teórico e necessidades metodológicas do projeto.
Versão em BibTeX: [referencias.bib](referencias.bib).

BANCO CENTRAL DO BRASIL. **Pix**: arranjo de pagamentos instantâneos. Brasília: Banco
Central do Brasil, 2024. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/pix.
Acesso em: 16 maio 2026.

BANCO CENTRAL DO BRASIL. **Relatório de Gestão do Pix**. Brasília: Banco Central do
Brasil, 2024. Disponível em: https://www.bcb.gov.br/. Acesso em: 16 maio 2026.

BISHOP, Christopher M. **Pattern Recognition and Machine Learning**. New York: Springer,
2006.

DIESTEL, Reinhard. **Graph Theory**. 5. ed. Berlin: Springer, 2017.

EASLEY, David; KLEINBERG, Jon. **Networks, Crowds, and Markets**: reasoning about a
highly connected world. New York: Cambridge University Press, 2010.

ESTER, Martin; KRIEGEL, Hans-Peter; SANDER, Jörg; XU, Xiaowei. A density-based algorithm
for discovering clusters in large spatial databases with noise. In: INTERNATIONAL
CONFERENCE ON KNOWLEDGE DISCOVERY AND DATA MINING, 2., 1996, Portland. **Proceedings**
[...]. Portland: AAAI Press, 1996. p. 226-231.

JAMES, Gareth; WITTEN, Daniela; HASTIE, Trevor; TIBSHIRANI, Robert. **An Introduction to
Statistical Learning**. 2. ed. New York: Springer, 2021.

LIU, Fei Tony; TING, Kai Ming; ZHOU, Zhi-Hua. Isolation Forest. In: IEEE INTERNATIONAL
CONFERENCE ON DATA MINING, 8., 2008, Pisa. **Proceedings** [...]. Pisa: IEEE, 2008.
p. 413-422.

WITTEN, Ian H.; FRANK, Eibe; HALL, Mark A. **Data Mining**: practical machine learning
tools and techniques. 3. ed. Burlington: Morgan Kaufmann, 2011.

### Cursos e materiais complementares

- Udemy: *Machine Learning e Data Science com Python de A a Z*. Curso usado como apoio
  complementar para conceitos de aprendizado de máquina e análise de dados. Acesso em:
  16 maio 2026.
- Udemy: *Teoria dos Grafos para Computação*. Curso complementar para estudo de modelagem
  de redes, métricas estruturais e aplicações computacionais. Acesso em: 16 maio 2026.
- Coursera: *Machine Learning Specialization*. Curso gratuito (modo auditoria) usado como
  apoio teórico em técnicas de aprendizado de máquina. Acesso em: 16 maio 2026.
- Kaggle Learn: *Intro to Machine Learning*. Plataforma gratuita usada para estudos
  introdutórios de aprendizado de máquina e análise de dados. Acesso em: 16 maio 2026.
- freeCodeCamp. Plataforma gratuita usada como apoio complementar em Python, ciência de
  dados e visualização de dados. Acesso em: 16 maio 2026.
