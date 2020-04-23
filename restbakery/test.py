#!/usr/bin/env python3

from .models import ModelBase
from .fields import *
from .complexfields import *

import unittest

class A(ModelBase):
	id = CharField(default='hello')

class B(A):
	char_field = CharField()
	str_array_field = ArrayField(str)
	cls_array_field = ArrayField(A)

class TestObjectSetupMethods(unittest.TestCase):


	def setUp(self):
		self.a = A()
		self.b = B()

	def test_attribute_setup_a(self):
		self.assertTrue(hasattr(self.a, 'id'))
		self.assertEqual(type(self.a.id), str)
		self.assertEqual(self.a.id, 'hello')
		self.assertIn('id', self.a._base_fields)
		self.assertEqual(type(self.a._base_fields['id']), CharField)
		self.assertTrue('char_field' not in A._base_fields)
		self.assertFalse(hasattr(self.a, 'char_field'))

	def test_attribute_setup_b(self):
		self.assertTrue(hasattr(self.b, 'char_field'))

	def test_id_is_different_a_b(self):
		self.a.id = 'a1'
		self.b.id = 'b1'
		self.assertTrue(self.a.id != self.b.id)

	def test_id_is_different_a_a(self):
		self.a.id = 'a1'
		aa = A()
		aa.id = 'a2'
		self.assertTrue(self.a.id != aa.id)

class TestCharField(unittest.TestCase):
	class CFTest(ModelBase):
		id = CharField()

	def setUp(self):
		self.a = A()
		self.cftest = TestCharField.CFTest()

	def test_set_default(self):
		self.assertEqual(self.cftest.id, CharField.default)

	def test_overwrite_default(self):
		self.assertEqual(self.a.id, 'hello')

	def test_serialize_field(self):
		self.assertEqual(self.a.serialize(), {'id': 'hello'})

class TestDictField(unittest.TestCase):
	class DictFieldTest(ModelBase):
		id = DictField()

	def setUp(self):
		self.a = TestDictField.DictFieldTest()

	def test_set_default(self):
		self.assertTrue(isinstance(self.a.id, dict))

	def test_default_callable(self):
		b = TestDictField.DictFieldTest()
		self.assertNotEqual(hex(id(self.a.id)), hex(id(b.id)))

	def test_set_value(self):
		self.a.id['foo'] = 'bar'
		self.assertEqual(self.a.id, {'foo': 'bar'})

	def test_serialize_field(self):
		self.a.id['foo'] = 'bar'
		self.assertEqual(self.a.serialize(), {'id': {'foo': 'bar'}})

if __name__ == '__main__':
    unittest.main()