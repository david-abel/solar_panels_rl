import tensorflow as tf

# ====================
# == Layer wrappers ==
# ====================

def conv2d(x, W, strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
    return tf.nn.relu(x)

def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1], padding='SAME')

def conv_net(x, weights):
    # MNIST data input is a 1-D vector of 784 features (28*28 pixels)
    # Reshape to match picture format [Height x Width x Channel]
    # Tensor input become 4-D: [Batch Size, Height, Width, Channel]
    x = tf.reshape(x, shape=[-1, 28, 28, 1])

    # Convolution Layer
    conv1 = conv2d(x, weights['wc1'])
    
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1, k=2)

    # Convolution Layer
    conv2 = conv2d(conv1, weights['wc2'])
    
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2, k=2)

    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.matmul(fc1, weights['wd1'])
    fc1 = tf.nn.relu(fc1)

    # Output, class prediction
    out = tf.matmul(fc1, weights['out'])

    return out

# ======================
# == Weights & Biases ==
# ======================

# Network Parameters
num_input = 784 # Image Size (img shape: 28*28)
num_bandit_arms = 10

# Training Parameters
learning_rate = 0.0001
num_steps = 200
batch_size = 128

# tf Graph input
X = tf.placeholder(dtype=tf.float32, shape=[None, num_input])
Y = tf.placeholder(dtype=tf.float32, shape=[None, num_bandit_arms])

# Store layers weight & bias
weights = {
    # 5x5 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
    # 5x5 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    'wd1': tf.Variable(tf.random_normal([7*7*64, 1024])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, num_bandit_arms]))
}

# Construct model
logits = conv_net(X, weights)
softmax_prediction = tf.nn.softmax(logits)
prediction = tf.argmax(logits, 1)

# Define loss and optimizer
# loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y))
loss_op = tf.reduce_mean(tf.losses.mean_squared_error(softmax_prediction, Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
train_op = optimizer.minimize(loss_op)

# Evaluate model
correct_pred = tf.equal(tf.argmax(softmax_prediction, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# GPU Params.
config = tf.ConfigProto(allow_soft_placement=True)
config.gpu_options.allow_growth = True
sess = tf.Session(config=config) # Sessions allow you to initialize variables and pump vals into variables.
sess.run(tf.initialize_all_variables()) # tf.init_all_Vars puts things into gpu.
