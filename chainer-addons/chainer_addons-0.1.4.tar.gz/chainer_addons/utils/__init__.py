
def all_children(model):
	"""
		Iterate over all links in a (nested) chain.
	"""

	for child in model.children():
		grand_children = list(child.children())
		if grand_children:
			for grand_child in all_children(child):
				yield grand_child
		else:
			yield child
