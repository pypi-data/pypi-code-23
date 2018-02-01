"""
here you can find some model definitions or modificated versions
of present models in chainer (eg. VGG19)
"""
import chainer
import chainer.functions as F

from inspect import signature


def do_call(func, *args, **kw):
	sig = signature(func)
	train = kw.pop("train", True)
	if "train" in sig.parameters: 	kw["train"] = train
	elif "test" in sig.parameters:	kw["test"]  = not train

	return func(*args, **kw)

class Classifier(chainer.Chain):
	"""
		model wrapper, that is adapted for the DSL of
		the pretrained models in chainer
	"""
	def __init__(self, model, layer_name):
		super(Classifier, self).__init__()
		with self.init_scope():
			self.model = model

		self.layer_name = layer_name

	def __call__(self, X, y):
		activations = self.model(X, layers=[self.layer_name])
		pred = activations[self.layer_name]

		loss, accu = F.softmax_cross_entropy(pred, y), F.accuracy(pred, y)
		chainer.report({
			"loss": loss.data,
			"accuracy": accu.data,
		}, self)
		return loss

class PretrainedModelMixin(object):
	def __call__(self, X, layer_name):
		activations = super(PretrainedModelMixin, self).__call__(X, layers=[layer_name])
		return activations[layer_name]


from chainer_addons.models.vgg import VGG19Layers
from chainer_addons.models.resnet import ResnetLayers
