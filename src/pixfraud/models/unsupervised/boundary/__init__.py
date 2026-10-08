"""Modelos de **fronteira**: uma superfície envolve as contas normais, e a suspeita fica do lado de fora.

* ``one_class_svm``: a fronteira de um SVM de uma classe, com núcleo RBF.
"""

from pixfraud.models.unsupervised.boundary.one_class_svm import one_class_svm

__all__ = ["one_class_svm"]
