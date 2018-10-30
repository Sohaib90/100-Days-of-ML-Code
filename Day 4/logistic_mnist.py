import tensorflow as tf 
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)


# inference of a simple logistic regression on mnist dataset
# where an input multiplies with weight and bias to get z(logit) which is then passed through softmax function for non-linearity
def inference(x) :
	init = tf.constant_initializer(value=0)
	W = tf.get_variable("W", [784,10], initializer = init)
	b = tf.get_variable("b",[10], initializer=init)

	output= tf.nn.softmax(tf.matmul(x,W)+b)
	return output

# cross entropy loss of the batch
def loss(output,y):
	dot_product = y * tf.log(output)

	xentropy = -tf.reduce_sum(dot_product,reduction_indices=1)
	loss = tf.reduce_mean(xentropy)
	return loss

# optimizer which will reduce the error and update gradients
def training(cost, global_step):
	tf.summary.scalar("cost",cost)

	optimizer = tf.train.GradientDescentOptimizer(learning_rate)
	train_op = optimizer.minimize(cost,global_step=global_step)
	return train_op

#evaluation of the model
def evaluation(output,y):
	correct_pred = tf.equal(tf.argmax(output,1),tf.argmax(y,1))
	accuracy = tf.reduce_mean(tf.cast(correct_pred,tf.float32))
	return accuracy

#Parameters 
learning_rate = 0.01
training_epochs = 1000
batch_size = 100
display_step =1

with tf.Graph().as_default():

	#mnist data image of 28*28=784
	x = tf.placeholder("float",[None,784])

	#digits recognition placeholder
	y = tf.placeholder("float",[None,10])

	output = inference(x)
	cost = loss(output,y)
	global_step = tf.Variable(0,name="global_step",trainable=False)

	train_op = training(cost,global_step)
	eval_op = evaluation(output,y)

	summary_op = tf.summary.merge_all()

	saver = tf.train.Saver()
	sess = tf.Session()
	summary_writer = tf.summary.FileWriter("logistic_logs/",graph_def = sess.graph_def)

	init_op = tf.initialize_all_variables()

	sess.run(init_op)

	#Training Cycle

	for epoch in range(training_epochs):

		avg_cost = 0
		total_batch = int(mnist.train.num_examples/batch_size)

		#Loop over all batches
		for i in range(total_batch):
			mbatch_x, mbatch_y = mnist.train.next_batch(batch_size)

			feed_dict = {x: mbatch_x, y:mbatch_y}
			sess.run(train_op, feed_dict= feed_dict)

			minibatch_cost = sess.run(cost, feed_dict= feed_dict)
			avg_cost += minibatch_cost/total_batch

			if epoch%display_step == 0 :
				val_feed_dict = {
					x: mnist.validation.images,
					y: mnist.validation.labels
				}

				accuracy = sess.run(eval_op, feed_dict=val_feed_dict)
				print( "Validation error: {} ".format(1-accuracy))

				summary_str = sess.run(summary_op,feed_dict=feed_dict)

				summary_writer.add_summary(summary_str,sess.run(global_step))

				saver.save(sess, "logistic_logs/model-checkpoint", global_step = global_step)

	print ("Optimization Finished")

	test_feed_dict = {
		x: mnist.test.images,
		y: mnist.test.labels
	}

	accuracy = sess.run(eval_op, feed_dict = test_feed_dict)

	print ("Testing accuracy: {}".format(accuracy))
