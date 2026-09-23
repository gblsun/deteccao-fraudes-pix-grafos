---
tags: [glossario]
---

# Local Outlier Factor (LOF)

Compara a densidade em volta de uma conta com a densidade em volta dos seus vizinhos, em
vez de usar um raio único para toda a base como o [DBSCAN](dbscan-e-k-distance.md). Acha
anomalias **locais**: uma conta pode estar numa região esparsa sem ser anômala, se seus
vizinhos também estão espalhados.

$$\text{LOF}(v) = \frac{1}{k}\sum_{u \in N_k(v)} \frac{\text{densidade}(u)}{\text{densidade}(v)}$$

LOF $\approx 1$: densidade igual aos vizinhos. Quanto maior, mais isolada a conta.

**Cuidado.** Com muitas contas de atributos idênticos (comum nos nossos conjuntos
temporais, em janelas curtas), a densidade local degenera e o escore pode disparar; o
scikit-learn avisa quando isso acontece.

**No projeto.** [`anomaly.local_outlier_factor`](../../src/pixfraud/anomaly.py), o
terceiro detector, registrado em `DETECTORS`.
