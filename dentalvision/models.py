from __future__ import annotations

from tensorflow.keras import Model, Sequential
from tensorflow.keras.applications import EfficientNetB0, MobileNet, ResNet50
from tensorflow.keras.layers import (
    BatchNormalization,
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    GlobalAveragePooling2D,
    Input,
    MaxPooling2D,
)


def build_cnn(input_shape: tuple[int, int, int], num_classes: int) -> Model:
    model = Sequential(
        [
            Input(shape=input_shape),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D(pool_size=(2, 2)),
            BatchNormalization(),
            Conv2D(128, (3, 3), activation="relu"),
            MaxPooling2D(pool_size=(2, 2)),
            BatchNormalization(),
            Conv2D(256, (3, 3), activation="relu"),
            MaxPooling2D(pool_size=(2, 2)),
            BatchNormalization(),
            Flatten(),
            Dense(512, activation="relu"),
            Dropout(0.5),
            Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def build_transfer_model(
    backbone_name: str, input_shape: tuple[int, int, int], num_classes: int
) -> Model:
    if backbone_name == "MobileNet":
        base_model = MobileNet(weights="imagenet", include_top=False, input_shape=input_shape)
    elif backbone_name == "ResNet50":
        base_model = ResNet50(weights="imagenet", include_top=False, input_shape=input_shape)
    elif backbone_name == "EfficientNetB0":
        base_model = EfficientNetB0(weights="imagenet", include_top=False, input_shape=input_shape)
    else:
        raise ValueError(f"Unsupported backbone: {backbone_name}")

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.5)(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=base_model.input, outputs=outputs)

    for layer in base_model.layers:
        layer.trainable = False

    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


MODEL_REGISTRY: dict[str, callable] = {
    "Improved_CNN": build_cnn,
    "MobileNet": lambda input_shape, num_classes: build_transfer_model(
        "MobileNet", input_shape, num_classes
    ),
    "ResNet50": lambda input_shape, num_classes: build_transfer_model(
        "ResNet50", input_shape, num_classes
    ),
    "EfficientNetB0": lambda input_shape, num_classes: build_transfer_model(
        "EfficientNetB0", input_shape, num_classes
    ),
}


def build_model(model_name: str, input_shape: tuple[int, int, int], num_classes: int) -> Model:
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {model_name}. Available: {list(MODEL_REGISTRY.keys())}")
    if model_name == "Improved_CNN":
        return MODEL_REGISTRY[model_name](input_shape, num_classes)
    return MODEL_REGISTRY[model_name](input_shape, num_classes)
