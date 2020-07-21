import tensorflow as tf
from models import ConvBN, ResNetBlock, BottleNeckBlock


class ResNet:
    init_channel = 64
    layer_components = {
        10: [1, 1, 1, 1], #Custom ResNet
        18: [2, 2, 2, 2],
        34: [3, 4, 6, 3],
        50: [3, 4, 6, 3],
        101: [3, 4, 23, 3],
        152: [3, 8, 36, 3]
    }

    def __init__(self, input_shape=(None, None, 3), n_classes=0, n_layer=18):
        """

        :param input_shape: (tuple) (h, w, c)
        :param n_classes: If 0 is given, top_layer will not be included.
        :param n_layer: 18, 34, 50, 101, 152
        """
        assert n_layer in list(ResNet.layer_components.keys())
        self.input_shape = input_shape
        self.n_classes = n_classes
        self.n_layer = n_layer
        self.layer_component = ResNet.layer_components[self.n_layer]

    def get_layer(self, input_layer):
        ResBlock = ResNetBlock if self.n_layer < 50 else BottleNeckBlock

        layer = ConvBN(ResNet.init_channel, (7, 7), strides=(2, 2), name="stem")(input_layer)
        layer = tf.keras.layers.MaxPool2D((3, 3), strides=(2, 2), padding='SAME', name="max_pool")(layer)

        for i, n_layer in enumerate(self.layer_component):
            channel = ResNet.init_channel * (2**i)

            for j in range(n_layer):
                downsample = True if (i > 0 and j == 0) else False
                layer = ResBlock(channel, (3, 3), downsample=downsample, name=f"resblock_{i}_{j}")(layer)

        if self.n_classes > 0:
            layer = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(layer)
            layer = tf.keras.layers.Dense(self.n_classes, activation='softmax', use_bias=True, name="out_dense")(layer)

        return layer

    def build_model(self, input_layer=None):
        if input_layer is None:
            input_layer = tf.keras.layers.Input(self.input_shape)

        layer = self.get_layer(input_layer)

        model = tf.keras.models.Model(input_layer, layer)

        return model

class ResNet18(ResNet):
    def __init__(self, input_shape=(None, None, 3), n_classes=0, include_top=False, weights=None):
        ResNet.__init__(self, input_shape=input_shape, n_classes=n_classes, n_layer=18)
        self.n_classes = 0 if include_top is False else n_classes
        self.weights = weights


class ResNet10(ResNet):
    def __init__(self, input_shape=(None, None, 3), n_classes=0, include_top=False, weights=None):
        ResNet.__init__(self, input_shape=input_shape, n_classes=n_classes, n_layer=10)
        self.n_classes = 0 if include_top is False else n_classes
        self.weights = weights


if __name__ == "__main__":
    resnet = ResNet(input_shape=(224, 224, 3), n_classes=10, n_layer=18)
    model = resnet.build_model()
