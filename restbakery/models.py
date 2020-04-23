import logging

from .fields import BaseField, ComplexField


logger = logging.getLogger('restbakery')


class Serializable:
	pass





class ClsTemplate(type):
	def __new__(cls, name, bases, dct):
		# Bypass regular attribute creation for attr of type 
		# BaseField (or child)
		logger.debug(f"C__new {name} with bases {bases} and dct {dct}")

		# step 1: determine all attrs of type BaseField
		#         and store in temp structure
		tmp_base_fields = {}
		for key, field in dct.items():
			if isinstance(field, BaseField):
				tmp_base_fields[key] = field
		
		# step 2: remove attrs of type BaseField from dct
		for key in tmp_base_fields.keys():
			dct.pop(key)
		
		# step 3: create instance without attributes of
		#         type BaseField
		instance = super().__new__(cls, name, bases, dct)

		# step 4: add all fields from base classes
		#         create it (type dict)
		# if not hasattr(instance, '_base_fields'):
		instance._base_fields = {}
		for base_cls in bases:
			base_cls_base_fields = getattr(base_cls, '_base_fields', {})
		instance._base_fields.update(base_cls_base_fields)
		
		# step 5: add attrs of type BaseField to 
		#         cls._base_fields dict
		instance._base_fields.update(tmp_base_fields)

		# step 6: set var name. Note: this has to be called 'manually'
		#		  here, since the fields are not added as normal class attrs
		for field_name, field in instance._base_fields.items():
			field.__set_name__(instance, field_name)
		
		logger.debug(f"C__new {name} with bases {bases} and dct {dct} (id {hex(id(instance))})")
		return instance

	# def __init__(cls, name, bases, dct):
	# 	logger.debug(f"C__init {name} with bases {bases} and dct {dct}")
	# 	super().__init__(name, bases, dct)
	# 	# logger.debug(klass_fields(cls))

	# def __setattr__(cls, attr, value):
	# 	logger.debug(f"C__setattr {attr} on {cls} to {value}")
	# 	super().__setattr__(attr, value)

def klass_fields(cls):
	all_cls_fields = dict(cls.__dict__)
	for base_cls in [bcls for bcls in cls.__bases__ if isinstance(bcls, ModelBase)]:
		all_cls_fields.update(klass_fields(base_cls))
	cls_base_fields = {field_name:field for field_name,field in all_cls_fields.items() if isinstance(field, BaseField) }
	return cls_base_fields


class ModelBase(Serializable, metaclass=ClsTemplate):

	def __init__(self, **kwargs):
		logger.debug(f"{self} has fields {self._base_fields}")
		# add a cloned version of all _base_fields to the instance
		for field_name, field in self._base_fields.items():
			logger.debug(f"__init modelbase of cls {self.__class__.__name__} for field {field_name} with {field} of type {type(field)}")
			initval = kwargs.get(field_name, field.get_default())
			setattr(self, field_name, initval)
		super().__init__()

	def __setattr__(self, name, value):
		# Check if the field to be set is defined for the model
		logger.debug(f"__setattr {name} to {value}")
		if name not in self._base_fields:
			raise TypeError(f"no field {name} in model {self.__class__}")

		# Actual assignment is done by parent method
		# super().__setattr__(name, value)
		self._base_fields[name].__set__(self, value) 

	def serialize(self):
		# Create a dict containing all members of type
		# BaseField
		# fields = dict(self._get_fields())
		# fields = {}
		# for key in self._base_fields.keys():
		# 	print(key)
		# 	fields[key] = getattr(self, key)
		content = {}
		for name, field in self._base_fields.items():
			logger.debug(f"serializing {name} ({field}) of {self}")
			# val = self._base_fields[name].__get__(self)
			val = self._base_fields[name].serialize(self)
			# We only consider fields of type BaseField
			# if hasattr(val, 'serialize'):
				# logger.debug('ComplexField',field)
				# val = val.serialize()
			# else:
				# Get the value of the field 'name'
				# val = getattr(self, name)
			content[name] = val
		return content

	# def _get_fields(self):
	# 	fields = [(field_name, field) for field_name,field in self.__dict__.items() if isinstance(field, BaseField)]
	# 	return fields