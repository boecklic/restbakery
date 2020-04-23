import logging
logger = logging.getLogger('restbakery')

class BaseField(object):
	default = None
	"""Implemented as descriptor:
	see https://docs.python.org/3/howto/descriptor.html
	for details"""
	def __init__(self, default=None, var_name=None, null=True):
		if default is None:
			self._default = self.__class__.default
		else:
			self._default = default
		self.var_name = var_name
		self.null = null


	def get_default(self):
		if callable(self._default):
			return self._default()
		else:
			return self._default
	
	def serialize(self, instance, owner=None):
		val = self.__get__(instance)
		# If the val has a serialize method, we call it to get
		# the serialized value, otherwise we take the value itself
		if hasattr(val, 'serialize'):
			val = val.serialize()
		return val

	def __get__(self, instance=None, owner=None):
		logger.debug(f"__get '{self.var_name}' from {self}")
		# return self.val
		try:
			value = instance.__dict__[self.var_name]
		except KeyError as e:
			logger.error(f"{instance} has no field {self.var_name} (only: {instance.__dict__}")
			raise
		return value

	def __set__(self, instance, value):
		logger.debug(f"__set '{self.var_name}' (field id {hex(id(self))}) on {instance} to {value}")

		if not isinstance(value, BaseField) \
		   and not isinstance(value, self.typ) \
		   and not self.null:
			raise TypeError(f"expecting type {self.typ} instead of {type(value)}")
		# logger.debug(self.var_name)
		# logger.debug(dir(self))
		logger.debug(type(instance))
		# self.val = value
		try:
			instance.__dict__[self.var_name] = value
		except KeyError as e:
			logger.error(f"{instance} has no field {self.var_name} (only: {instance.__dict__}")
			raise

	def __set_name__(self, owner, name):
		logger.debug(f"{self.__class__} was added to {owner} as {name}")
		self.var_name = name
		self.owner = owner


class ComplexField(BaseField):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class CharField(BaseField):
	typ = str
	default = ''


class IntField(BaseField):
	typ = int
	default = 0


class BooleanField(BaseField):
	typ = bool
	default = False


class DictField(BaseField):
	typ = dict
	# Note: default must be callable otherwise all fields
	# would use the same dict
	default = dict