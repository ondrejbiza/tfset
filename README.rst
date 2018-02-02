tfset
=====

.. figure:: tfset/images/validation_curve.png
   :alt: Validation Curve

**Change the hyper-parameters** of your Tensorflow training session on
the fly. The package allows you to schedule events that change the
values of arbitrary Tensors with a simple command.

Requirements
~~~~~~~~~~~~

-  Python >= 3
-  tensorflow >= 1.0

Set Up
~~~~~~

Install the package with pip:

``pip install tfset``

Or clone and install from github:

.. code-block:: bash

   git clone https://github.com/ondrejba/tfset.git
   cd tfset
   python setup.py install

Usage
~~~~~

tfset DEMO
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check
`MNIST\_demo.ipynb <https://github.com/ondrejba/tfset/blob/master/MNIST_demo.ipynb>`__
for a demostration of the usage of tfset in a simple
training script.

Server
^^^^^^

Import tfset server.

::

    import tfset.server as server

Create Tensors for your hyper-parameters.

::

    learning_rate = tf.get_variable("learning_rate", initializer=tf.constant(0.1, dtype=tf.float32))
    dropout_prob = tf.get_variable("dropout_prob", initializer=tf.constant(0.9, dtype=tf.float32))

Create and start a Session Server.

::

    # "session" is a Tensorflow session
    s, thread = server.run_server([learning_rate, dropout_prob], session)

Periodically check for events.

::

    # "step" is the global step of your training procedure
    s.check_events(step)

Stop the server.

::

    s.shutdown()
    thread.join(timeout=10)

Client
^^^^^^

Get status.

``tfset -s``

Add an event (this event sets the learning rate to 0.01 at iteration
10000).

``tfset -a -n learning_rate:0 -i 10000 --value 0.01``

Remove an event (with index 0 in this case).

``tfset -r -e 0``

Events
^^^^^^

tfset schedules hyper-parameter changes based on
**events**. An event contains the following information:

-  **iteration**: when to execute the event
-  **Tensor name**: which Tensor to change
-  **value**: value to set the Tensor to

The reason for the use of events is that you might want to schedule
hyper-parameter changes in the future (e.g. lower learning rate to 10e-3
at 800k iteration). If two events targeting the same Tensor are
scheduled at the same iteration, the one that was scheduled later is
going to be executed.
