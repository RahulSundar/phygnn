"""
Tests for basic phygnn functionality and execution.
"""
# pylint: disable=W0613
import numpy as np
import pandas as pd
import pytest

from phygnn.model_interfaces.tf_model import TfModel


N = 100
A = np.linspace(-1, 1, N)
B = np.linspace(-1, 1, N)
A, B = np.meshgrid(A, B)
A = np.expand_dims(A.flatten(), axis=1)
B = np.expand_dims(B.flatten(), axis=1)

Y = np.sqrt(A ** 2 + B ** 2)
X = np.hstack((A, B))
features = pd.DataFrame(X, columns=['a', 'b'])
labels = pd.DataFrame(Y, columns=['c'])


@pytest.mark.parametrize(
    ('hidden_layers', 'loss'),
    [(None, 0.6),
     ([{'units': 64, 'activation': 'relu', 'name': 'relu1'},
       {'units': 64, 'activation': 'relu', 'name': 'relu2'}], 0.008)])
def test_nn(hidden_layers, loss):
    """Test TfModel """
    model = TfModel.train(features, labels,
                          hidden_layers=hidden_layers,
                          epochs=10,
                          fit_kwargs={"batch_size": 16},
                          early_stop=False)

    n_l = len(hidden_layers) * 2 + 1 if hidden_layers is not None else 1
    n_w = (len(hidden_layers) + 1) * 2 if hidden_layers is not None else 2
    assert len(model.layers) == n_l
    assert len(model.weights) == n_w
    assert len(model.history) == 10

    test_mae = np.mean(np.abs(model[X].values - Y))
    assert model.history['val_mae'].values[-1] < loss
    assert test_mae < loss


@pytest.mark.parametrize(
    ('normalize', 'loss'),
    [(True, 0.04),
     (False, 0.002),
     ((True, False), 0.002),
     ((False, True), 0.02)])
def test_normalize(normalize, loss):
    """Test TfModel """
    hidden_layers = [{'units': 64, 'activation': 'relu', 'name': 'relu1'},
                     {'units': 64, 'activation': 'relu', 'name': 'relu2'}]
    model = TfModel.train(features, labels,
                          normalize=normalize,
                          hidden_layers=hidden_layers,
                          epochs=10, fit_kwargs={"batch_size": 16},
                          early_stop=False)

    test_mae = np.mean(np.abs(model[X].values - Y))
    assert model.history['val_mae'].values[-1] < loss
    assert test_mae < loss


def test_complex_nn():
    """Test complex TfModel """
    hidden_layers = [{'units': 64, 'activation': 'relu', 'dropout': 0.01},
                     {'units': 64},
                     {'batch_normalization': {'axis': -1}},
                     {'activation': 'relu'},
                     {'dropout': 0.01}]
    model = TfModel.train(features, labels,
                          hidden_layers=hidden_layers,
                          epochs=10, fit_kwargs={"batch_size": 16},
                          early_stop=False)

    assert len(model.layers) == 8
    assert len(model.weights) == 10

    test_mae = np.mean(np.abs(model[X].values - Y))
    loss = 0.07
    assert model.history['val_mae'].values[-1] < loss
    assert test_mae < loss
