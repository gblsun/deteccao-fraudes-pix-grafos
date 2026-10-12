---
tags: [glossario]
---

# Otimização de hiperparâmetros

**Hiperparâmetros** são as escolhas feitas *antes* de o modelo rodar: o número de vizinhos
do kNN, o número de grupos do k-means, a profundidade das árvores. Otimizar é testar várias
escolhas e ficar com a de melhor nota ([average precision](average-precision.md)).

**Busca em grade.** Uma lista de valores por hiperparâmetro (por exemplo, 2, 4, 8 e 16
grupos), e todas as combinações são testadas.

**O limite da grade.** Se o vencedor é o último valor da lista, não dá para saber se um
valor maior seria ainda melhor: a tendência "quanto mais, melhor" pode continuar além do
que foi testado. Quando o vencedor fica **no meio** da lista, os dois lados foram testados e
pioraram. A busca do projeto **se amplia sozinha**: quando o vencedor cai na ponta, ela
acrescenta o próximo valor no mesmo passo multiplicativo (50 e 100 levam a testar 200) e
testa de novo, até o vencedor ficar no meio ou bater num limite que não faz sentido passar
(uma fração não passa de 1, por exemplo).

**Validação × teste: sem trapaça.** A nota usa o gabarito, então escolher e avaliar nas
mesmas redes inflaria o resultado, como estudar com a prova que vai cair. Os
hiperparâmetros são escolhidos em redes de **validação** ([sementes](semente.md) 1001 em
diante) e avaliados nas de **teste** (sementes 1 a 10), que nunca entram na escolha.
Quanto mais combinações se testa, maior a chance de o vencedor ser o mais sortudo na
validação; é por isso que só o teste conta.

**No projeto.** O subpacote [`tuning/`](../../src/pixfraud/tuning/__init__.py), as grades em
[`configs/busca_hiperparametros.yaml`](../../configs/busca_hiperparametros.yaml) e o script
`scripts/03_modelos/otimizar_hiperparametros.py`. O resultado, antes e depois, está no
[mapa dos modelos](../../src/pixfraud/models/mapa-dos-modelos.md).
