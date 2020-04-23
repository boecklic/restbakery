import logging
from enum import Enum

from .models import ModelBase
from .fields import BaseField, ComplexField

logger = logging.getLogger('restbakery')



class ModelField(ComplexField):

	def __init__(self, typ):
		if ModelBase not in typ.__bases__:
			raise TypeError(f"ModelField can only be used to store child types of ModelBase, not {type(typ)}")
		self.typ = typ
		super().__init__()

	# def serialize(self):
	# 	return self.val.serialize()

	# def clone(self):
	# 	clo = self.__class__(self.typ)
	# 	return clo


class Array(list):

	def __init__(self, typ):
		logger.debug(f"__init Array of type {typ}")

		# Note: we cannot compare to 'type' since the type of the ModelField
		# class is not 'type' but a childclass of 'type' (ClsTemplate metaclass)
		if not isinstance(typ, type):
			raise TypeError(f"ArrayField must be initialized with an instance, not a class")
		# holds an array of type(typ) fields
		self._typ = typ
		super().__init__()
		# self._items = []

	def append(self, item):
		logger.debug(f"append {item} to {self}")
		# logger.debug("ids {}".format([getattr(ite, 'id',None) for ite in self._items]))
		logger.debug(getattr(item,'id',None))
		if type(item) != self._typ and self._typ not in item.__class__.__bases__:
			raise TypeError(f"only items of type {self._typ} may be appended to this field")
		# self._items.append(item)
		super().append(item)
		logger.debug(getattr(item,'id',None))
		# logger.debug('ids {}'.format([getattr(ite, 'id',None) for ite in self._items]))


	def serialize(self):
		# logger.debug(f"ArrayField.serialize ")
		serialized = []
		# logger.debug("self._items: {}".format([getattr(item,'id',None) for item in self._items]))
		for item in self:
			logger.debug(f"  - serializing {item} (type {type(item)}) of {self}")
			if hasattr(item, 'id'):
				logger.debug(item.id )
			if hasattr(item, 'serialize'):
				_serialized_item = item.serialize()
			else:
				_serialized_item = item
			logger.debug(f"     -> {_serialized_item}")
			serialized.append(_serialized_item)
		return serialized


# class ArrayField(ComplexField):
# 	typ = Array

# 	def __init__(self, array_typ):
# 		self._array_typ = array_typ
# 		# initvalue for array field is an array
# 		# of objects of type 'typ'
# 		super().__init__(Array(array_typ))

# 	def serialize(self):
# 		serialized = []
# 		logger.debug(self.val._items,[getattr(item,'id',None) for item in self.val._items])
# 		for item in self.val._items:
# 			logger.debug(f"serializing {item}")
# 			if hasattr(item, 'id'):
# 				logger.debug(item.id )
# 			serialized.append(item.serialize())
# 		return serialized

# 	def clone(self):
# 		logger.debug(f"clone ArrayField of type {self._array_typ}")
# 		clo = self.__class__(self._array_typ)
# 		return clo


class ArrayField(ComplexField):
	typ = list

	def __init__(self, array_typ):
		self._array_typ = array_typ
		# self._items = []
		# initvalue for array field is an array
		# of objects of type 'typ'
		super().__init__()

	def get_default(self):
		return Array(typ=self._array_typ)

	# def serialize(self):
	# 	# logger.debug(f"ArrayField.serialize ")
	# 	serialized = []
	# 	logger.debug("self._items: {}".format([getattr(item,'id',None) for item in self._items]))
	# 	for item in self._items:
	# 		logger.debug(f"  - serializing {item} (type {type(item)}) of {self}")
	# 		if hasattr(item, 'id'):
	# 			logger.debug(item.id )
	# 		if hasattr(item, 'serialize'):
	# 			_serialized_item = item.serialize()
	# 		else:
	# 			_serialized_item = item
	# 		logger.debug(f"     -> {_serialized_item}")
	# 		serialized.append(_serialized_item)
	# 	return serialized


	# def append(self, item):
	# 	logger.debug(f"append '{item}' to {repr(self._items)}")
	# 	logger.debug("ids {}".format([getattr(ite, 'id',None) for ite in self._items]))
	# 	logger.debug(getattr(item,'id',None))
	# 	if type(item) != self._array_typ and self._array_typ not in item.__class__.__bases__:
	# 		raise TypeError(f"only items of type {self._array_typ} may be appended to this field")
	# 	self._items.append(item)
	# 	logger.debug(getattr(item,'id',None))
	# 	logger.debug('ids {}'.format([getattr(ite, 'id',None) for ite in self._items]))


	# def clone(self):
	# 	logger.debug(f"clone ArrayField of type {self._array_typ}")
	# 	clo = self.__class__(self._array_typ)
	# 	return clo



class LinkField(ComplexField):
	typ = ModelBase

	def serialize(self, instance, owner=None):
		# we're only interested in the id of the model object
		# and don't want to serialize the whole object
		model_object = self.__get__(instance)
		return model_object.id

class EnumField(ComplexField):
	typ = Enum

	def __init__(self, choices, default=None):
		# Enum Field must be initialized with an Enum
		# type class
		if Enum not in choices.__bases__:
			raise TypeError("EnumField must be initialized with an Enum")
		self.choices = choices

		# initialize to first element of enum if no 
		# default is provided
		if default is None:
			default = next(iter(self.choices))
		
		# default must be one of the choices provided
		if default not in self.choices:
			raise ValueError(f"default must be one of {self.choices}")
		super().__init__(default=default)

	def serialize(self, instance, owner=None):
		try:
			name = self.__get__(instance).name
		except:
			logger.error(f"Error while serializing {self.__class__} field of {self.owner}")
			raise
		return name

	# def clone(self):
	# 	return self.__class__(self.choices, default=self.val)

