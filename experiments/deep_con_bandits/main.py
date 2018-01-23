'''
main.py

Facilitates training and testing of a simple CNN on MNIST.

Adapted from:
    Project: https://github.com/aymericdamien/TensorFlow-Examples/
    By: Aymeric Damien
'''

# Python imports.
import numpy as np
import tensorflow as tf

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)
import network as nn

def train_model(num_steps=10000, batch_size=128, print_interval=10):
    '''
    Args:
        num_steps (int)
        batch_size (int)
        print_interval (int)
    '''

    for step in range(1, num_steps + 1):

        batch_x, batch_y = mnist.train.next_batch(batch_size)

        # Run optimization op (backprop).
        nn.sess.run(nn.train_op, feed_dict={nn.X: batch_x, nn.Y: batch_y})
        
        if step % print_interval == 0 or step == 1:
            # Calculate batch loss and accuracy.
            loss, train_acc = nn.sess.run([nn.loss_op, nn.accuracy], feed_dict={nn.X: batch_x, nn.Y: batch_y})


            test_acc = nn.sess.run(nn.accuracy, feed_dict={nn.X: mnist.test.images[:128], nn.Y: mnist.test.labels[:128]})

            # Debug individual image prediction/loss.
            rand_test_image = np.random.randint(1,1028)
            single_loss, single_acc = nn.sess.run([nn.loss_op, nn.accuracy], feed_dict={nn.X:mnist.test.images[rand_test_image - 1:rand_test_image], nn.Y:mnist.test.labels[rand_test_image - 1: rand_test_image]}), np.argmax(mnist.test.labels[rand_test_image - 1:rand_test_image])
            
            print "Step", step, "\n\tLoss:", round(loss, 2), "\n\tTrain Accuracy:", train_acc, "\n\tTest Accuracy:", test_acc
            print 
            print "\tLoss for image", rand_test_image
            print "\t  Guess:", nn.sess.run([nn.prediction], feed_dict={nn.X:mnist.test.images[:1]}),
            print "True Label:", np.argmax(mnist.test.labels[rand_test_image - 1:rand_test_image])
            print "\t  Loss:", single_loss, "   acc?", single_acc


def main():
    train_model()

if __name__ == "__main__":
    main()
