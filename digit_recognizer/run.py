#!/usr/bin/env python3
"""
An machine learning exercise with TensorFlow
"""

import tensorflow as tf
import numpy as np

from sklearn.model_selection import train_test_split

tf.logging.set_verbosity(tf.logging.INFO)


def cnn_model_fn(features, labels, mode):
    # input layer
    input_layer = tf.reshape(features["x"], [-1, 28, 28, 1])

    # Convolutional Layer #1
    conv1 = tf.layers.conv2d(
        inputs=input_layer,
        strides=(1, 1),
        filters=32,
        kernel_size=[3, 3],
        padding="same",
        activation=tf.nn.relu
    )

    # Convolutional Layer #2
    conv2 = tf.layers.conv2d(
        inputs=conv1,
        strides=(2, 2),
        filters=32,
        kernel_size=[5, 5],
        padding="same",
        activation=tf.nn.relu
    )

    # Convolutional Layer #3
    conv3 = tf.layers.conv2d(
        inputs=conv2,
        strides=(1, 1),
        filters=64,
        kernel_size=[3, 3],
        padding="same",
        activation=tf.nn.relu
    )

    # Convolutional Layer #4
    conv4 = tf.layers.conv2d(
        inputs=conv3,
        strides=(2, 2),
        filters=64,
        kernel_size=[5, 5],
        padding="same",
        activation=tf.nn.relu
    )

    # Dense Layer
    conv4_flat = tf.reshape(conv4, [-1, 7 * 7 * 64])
    dense = tf.layers.dense(
        inputs=conv4_flat,
        units=1024,
        activation=tf.nn.relu
    )

    # Logits Layer
    logits = tf.layers.dense(inputs=dense, units=10)

    # And below are copied from tutorial
    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
        # `logging_hook`.
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(
        labels=labels,
        logits=logits
    )

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step()
        )
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels,
            predictions=predictions["classes"]
        )
    }
    return tf.estimator.EstimatorSpec(
        mode=mode,
        loss=loss,
        eval_metric_ops=eval_metric_ops
    )


def main(argv):
    # Load training data
    data = np.load('data/train_X.npy').astype(np.float32)
    labels = np.load('data/train_y.npy').astype(np.int32)
    train_data, eval_data, train_labels, eval_labels = train_test_split(
        data, labels, random_state=0)

    classifier = tf.estimator.Estimator(cnn_model_fn)

    tensors_to_log = {"probabilities": "softmax_tensor"}
    logging_hook = tf.train.LoggingTensorHook(
        tensors=tensors_to_log,
        every_n_iter=50
    )

    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": train_data},
        y=train_labels,
        batch_size=100,
        num_epochs=None,
        shuffle=True
    )

    classifier.train(
        input_fn=train_input_fn,
        steps=100,
        hooks=[logging_hook]
    )

    eval_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": eval_data},
        y=eval_labels,
        num_epochs=1,
        shuffle=False
    )

    eval_results = classifier.evaluate(input_fn=eval_input_fn)
    print(eval_results)

    test_data = np.load('data/test_X.npy').astype(np.float32)
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={"x": test_data},
        num_epochs=1,
        shuffle=False
    )

    predictions = classifier.predict(test_input_fn)
    labels = [pred['classes'] for pred in predictions]
    probs = [pred['probabilities'] for i, pred in enumerate(predictions)]
    print(labels)
    print(probs)

if __name__ == '__main__':
    tf.app.run()
