from enum import Enum
import chainer
from chainer.optimizers import MomentumSGD, Adam, RMSprop
from chainer.training import extensions

class OptimizerType(Enum):
	SGD = 1
	RMSPROP = 2
	ADAM = 3
	Default = SGD

	@classmethod
	def as_choices(cls):
		return {e.name.lower(): e for e in cls}

	@classmethod
	def get(cls, key):
		key = key.lower()
		choices = cls.as_choices()
		return choices.get(key) if key in choices else cls.Default

def optimizer(opt_type_name, model, lr=1e-2, decay=9e-1, *args, **kw):
	opt_type = OptimizerType.get(opt_type_name)
	opt_cls = {
		OptimizerType.SGD: MomentumSGD,
		OptimizerType.RMSPROP: RMSprop,
		OptimizerType.ADAM: Adam,
	}.get(opt_type)

	opt_args = dict(alpha=lr) if opt_type == OptimizerType.ADAM else dict(lr=lr)
	kw.update(opt_args)
	opt = opt_cls(*args, **kw)
	opt.setup(model)
	if decay:
		opt.add_hook(chainer.optimizer.WeightDecay(decay))

	return opt

def lr_shift(opt, init, rate, target):
	attr = "alpha" if isinstance(opt, Adam) else "lr"

	return extensions.ExponentialShift(
		optimizer=opt, attr=attr,
		init=init, rate=rate, target=target)

def no_grad(arr):
	return arr.data if isinstance(arr, chainer.Variable) else arr
