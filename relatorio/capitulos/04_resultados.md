# Resultados

> **Rascunho** tirado de [`docs/resultados.md`](../../docs/resultados.md), onde estão os
> números completos, as figuras e as ressalvas. Reescreva com as suas palavras e escolha
> o que entra no relatório; cada afirmação aqui tem a tabela correspondente em
> `reports/results/`.

## Validação do dataset sintético

Comparado com as estatísticas abertas do Pix [@bcb2026dadosabertos], o gerador acerta a
ordem de grandeza da divisão entre pagamentos a pessoas e a empresas (40% contra 49%) e o
ticket médio dos pagamentos a empresas (R$ 99 contra R$ 114), mas usa valores menores nos
Pix entre pessoas (R$ 101 contra R$ 257). A taxa de fraude é cerca de 110 vezes a real
(~530 golpes a cada 100 mil Pix, contra ~5), inflada de propósito para haver exemplos
suficientes, e o valor dos golpes é **menor** que o real (R$ 305 contra R$ 2.277). Nos
dados do Banco Central, apenas 11% do valor contestado e aceito volta à vítima pelo MED, e
51% não volta por saldo insuficiente: o dinheiro já havia saído da conta.

## A comparação entre atributos tabulares e de grafo depende do gerador

No cenário `base`, os atributos tabulares parecem bastar: com o DBSCAN, alcançam average
precision 0,76, contra 0,44 dos atributos de grafo. Esse resultado, porém, vem de sinais
embutidos por construção. Ao desligar o horário dos golpes e a idade das contas
fraudulentas, a AP do tabular cai para 0,25, enquanto a dos atributos de grafo permanece
em 0,43, e a comparação se inverte: o grafo vence em todas as 10 sementes, com os dois
detectores (diferença de +0,28 no Isolation Forest e +0,19 no DBSCAN, p ajustado por Holm
de 0,02). O mesmo vale nos cenários seguintes, incluindo aquele em que os golpes têm o
valor de um Pix comum.

![Average precision por cenário](../../reports/figures/cenarios_average_precision.png)

O conjunto com todos os atributos e o DBSCAN é a abordagem mais robusta: tem a maior AP em
seis dos oito cenários e, no cenário mais realista, alcança 0,50 [0,45; 0,55], cerca de 80
vezes o acaso.

## Perfis de fraude

Cada papel da quadrilha tem uma assinatura diferente: a conta laranja repassa o dinheiro
quase na hora e tem vizinhança em estrela; o intermediário é extremo em quase todos os
atributos; a coletora recebe muito e não repassa. As vítimas não se distinguem das pessoas
comuns, e nenhum detector as sinaliza. Os atributos de grafo encontram todos os
intermediários e coletoras, mas as contas laranja são as mais difíceis: só os atributos
temporais encontram a maioria (79%).

## Detectar a tempo de bloquear o dinheiro

Rodando os detectores a cada seis horas e bloqueando cada conta quando ela é sinalizada, o
que separa as abordagens é o **atraso**: com atributos tabulares, a conta é sinalizada
cerca de 22 horas depois do golpe; com atributos temporais, em três horas, perto do limite
imposto pela frequência das execuções. A fração do dinheiro que ficaria retida acompanha
esse atraso (45% contra 83%, supondo que o dinheiro parado por mais de uma hora é sacado).

![Detecção a tempo](../../reports/figures/online_deteccao.png)

## Poucos rótulos rendem muito

Tratando 25% das contas fraudulentas como já conhecidas (o equivalente às contestações do
MED) e propagando risco pelo grafo a partir delas, a average precision nas contas ainda
desconhecidas sobe de 0,46 para 0,95 no cenário mais realista. Um Random Forest treinado
com todos os rótulos chega a 0,99, contra 0,53 do melhor detector não supervisionado, o
que mostra o quanto se perde por não ter rótulos.

## Validação externa

Sobre o AMLworld [@altman2023realistic], com a mesma configuração e sem reajuste, o
desempenho absoluto é baixo (a melhor AP é 2,7 vezes o acaso), mas a ordem entre as
abordagens se mantém: os atributos de grafo superam os tabulares nas quatro janelas
avaliadas. As tipologias encontradas são as que deixam marcas de vizinhança (espalha e
junta, leque); cadeias e padrões aleatórios passam quase despercebidos.
