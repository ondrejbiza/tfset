# Interactive Tensorflow #

![Validation Curve](images/validation_curve.png)

Interactive Tensorflow allows you to alter hyper-parameters during training. It contains a server that
handles updating the parameters and a client that communicates with the server.

### Requirements ###

* Python >= 3
* tensorflow >= 1.0

### Set Up ###

Clone the repository with either

`git clone https://github.com/ondrejba/interactive-tensorflow.git interactive_tensorflow`

or

`git submodule add https://github.com/ondrejba/interactive-tensorflow.git interactive_tensorflow`

if you want to clone to an existing git repository.

We change the name of the repository to interactive_tensorflow because Python does not like the
dash symbol when importing modules.

### Usage ###

#### Server ####

Create Tensors for your hyper-parameters.

```
learning_rate = tf.get_variable("learning_rate", initializer=tf.constant(0.1, dtype=tf.float32))
dropout_prob = tf.get_variable("dropout_prob", initializer=tf.constant(0.9, dtype=tf.float32))
```

Create and start a Session Server.

```
# "session" is a Tensorflow session
s, thread = server.run_server([learning_rate, dropout_prob], session)
```

Periodically check for events.

```
# "step" is the global step of your training procedure
s.check_events(step)
```

#### Client ####

Get status.

`python client.py -s`

Add an event.

`python client.py -a -n learning_rate:0 -i 10000 --value 0.01`

Remove an event.

`python clien.py -r -e 0`
