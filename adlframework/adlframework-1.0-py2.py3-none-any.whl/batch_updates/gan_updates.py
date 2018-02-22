def switch_trainability(network, **kwargs):
	'''
	Preconditions:
	network has both a generator and discriminator variable

	It will switch the trainability of the generator and discriminator in between batches.
	'''
	network.generator.trainable = not network.generator.trainable
	network.discriminator.trainable = not network.discriminator.trainable
	assert network.generator.trainable != network.discriminator.trainable, "Both generator and discriminator are trainable! Network was probably initialized incorrectly."