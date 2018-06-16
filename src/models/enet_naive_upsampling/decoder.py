# coding=utf-8
from keras.layers.convolutional import Conv2D, Conv2DTranspose, UpSampling2D
from keras.layers.core import Activation
from keras.layers.merge import add
from keras.layers.normalization import BatchNormalization


def bottleneck(encoder, output, upsample=False, reverse_module=False, momentum=0.9):
    internal = output // 4
    x = Conv2D(internal, (1, 1), use_bias=False)(encoder)
    x = BatchNormalization(momentum=momentum)(x)
    x = Activation('relu')(x)
    if not upsample:
        x = Conv2D(internal, (3, 3), padding='same', use_bias=True)(x)
    else:
        x = Conv2DTranspose(filters=internal, kernel_size=(3, 3), strides=(2, 2), padding='same')(x)
    x = BatchNormalization(momentum=momentum)(x)
    x = Activation('relu')(x)

    x = Conv2D(output, (1, 1), padding='same', use_bias=False)(x)

    other = encoder
    if encoder.get_shape()[-1] != output or upsample:
        other = Conv2D(output, (1, 1), padding='same', use_bias=False)(other)
        other = BatchNormalization(momentum=momentum)(other)
        if upsample and reverse_module is not False:
            other = UpSampling2D(size=(2, 2))(other)
        
    if upsample and reverse_module is False:
        decoder = x
    else:
        x = BatchNormalization(momentum=momentum)(x)
        decoder = add([x, other])
        decoder = Activation('relu')(decoder)

    return decoder


def build(encoder, nc, momentum=0.9):
    enet = bottleneck(encoder, 64, upsample=True, reverse_module=True, momentum=momentum)  # bottleneck 4.0
    enet = bottleneck(enet, 64, momentum=momentum)  # bottleneck 4.1
    enet = bottleneck(enet, 64, momentum=momentum)  # bottleneck 4.2
    enet = bottleneck(enet, 16, upsample=True, reverse_module=True, momentum=momentum)  # bottleneck 5.0
    enet = bottleneck(enet, 16, momentum=momentum)  # bottleneck 5.1

    enet = Conv2DTranspose(filters=nc, kernel_size=(2, 2), strides=(2, 2), padding='same')(enet)
    return enet
