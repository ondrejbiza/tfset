import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

import server

# create tensors for parameters
learning_rate = tf.get_variable("learning_rate", initializer=tf.constant(0.1, dtype=tf.float32))
dropout_prop = tf.get_variable("dropout_prop", initializer=tf.constant(0.9, dtype=tf.float32))
is_training = tf.placeholder(tf.bool, [])

num_iterations = 100000
mnist_data_path = "demo/data/mnist"
summary_path = "demo/summary"

# import MNIST
mnist = input_data.read_data_sets(mnist_data_path, one_hot=True)

# create the model (a simple convolutional network)
x = tf.placeholder(tf.float32, (None, 784))
y = tf.placeholder(tf.float32, (None, 10))

x_reshaped = tf.reshape(x, (-1, 28, 28, 1))

conv1 = tf.layers.conv2d(x_reshaped, filters=32, kernel_size=(3, 3), strides=(1, 1), activation=tf.nn.relu)
pool1 = tf.layers.max_pooling2d(conv1, pool_size=(2, 2), strides=(2, 2))

conv2 = tf.layers.conv2d(pool1, filters=64, kernel_size=(3, 3), strides=(1, 1), activation=tf.nn.relu)
pool2 = tf.layers.max_pooling2d(conv2, pool_size=(2, 2), strides=(2, 2))

conv3 = tf.layers.conv2d(pool2, filters=128, kernel_size=(3, 3), strides=(1, 1), activation=tf.nn.relu)
pool4 = tf.reduce_mean(conv3, reduction_indices=(1, 2))

dropout = tf.layers.dropout(pool4, rate=dropout_prop, training=is_training)

logits = tf.layers.dense(dropout, 10)

cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits))
train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(cross_entropy)

correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

init_op = tf.global_variables_initializer()

# create summary ops
train_summaries = tf.summary.merge([tf.summary.scalar("train_accuracy", accuracy),
                                    tf.summary.scalar("train_loss", cross_entropy),
                                    tf.summary.scalar("learning_rate", learning_rate)])
test_summaries = tf.summary.merge([tf.summary.scalar("test_accuracy", accuracy)])

# create a summary writer
summary_writer = tf.summary.FileWriter(summary_path)

with tf.Session() as sess:
  sess.run(init_op)

  # start the server
  s, thread = server.run_server([learning_rate, dropout_prop], sess)

  # training
  for step in range(num_iterations):
    batch_xs, batch_ys = mnist.train.next_batch(64)

    _, train_summary = sess.run([train_step, train_summaries], feed_dict={
      x: batch_xs,
      y: batch_ys,
      is_training: True
    })
    summary_writer.add_summary(train_summary, global_step=step)

    if step % 100 == 0 and step > 0:
      # check events
      s.check_events(step)

      # test model
      test_summary = sess.run(test_summaries, feed_dict={
        x: mnist.test.images,
        y: mnist.test.labels,
        is_training: False
      })
      summary_writer.add_summary(test_summary, global_step=step)

  # evaluation
  accuracy = sess.run(accuracy, feed_dict={
    x: mnist.test.images,
    y: mnist.test.labels,
    is_training: False
  })

print("\nTrained for %d iterations" % num_iterations)
print("Accuracy: %.2f%%" % (accuracy * 100))