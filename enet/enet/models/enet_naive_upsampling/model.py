# coding=utf-8
from __future__ import absolute_import, print_function

from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Activation, Reshape
from tensorflow.keras.models import Model

from . import encoder, decoder


def transfer_weights(model, weights=None):
    """
    Always trains from scratch; never transfers weights
    :param model: 
    :param weights:
    :return: 
    """
    print('ENet has found no compatible pretrained weights! Skipping weight transfer...')
    return model


def build(nc, w, h,
          loss='categorical_crossentropy',
          optimizer='adam',
          **kwargs):
    data_shape = w * h if None not in (w, h) else -1  # TODO: -1 or None?
    inp = Input(shape=(h, w, 3))
    enet = encoder.build(inp)
    enet = decoder.build(enet, nc=nc)
    name = 'enet_naive_upsampling'

    enet = Reshape((data_shape, nc))(enet)  # TODO: need to remove data_shape for multi-scale training

    enet = Activation('softmax')(enet)
    model = Model(inputs=inp, outputs=enet)

    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy', 'mean_squared_error'])

    return model, name
