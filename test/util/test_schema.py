import unittest

from multiply_ui.util.schema import TypeDef, PropertyDef


class TypeDefTest(unittest.TestCase):
    def test_primitives(self):
        self.assertIsNone(TypeDef(str, optional=True).validate(None))
        self.assertIsNone(TypeDef(int).validate(234))
        self.assertIsNone(TypeDef(float).validate(1.234))
        self.assertIsNone(TypeDef(str).validate('bibo'))
        self.assertIsNone(TypeDef(str, choices=['ernie', 'bibo', 'bert']).validate('bibo'))

        with self.assertRaises(ValueError) as cm:
            TypeDef(int).validate(None)
        self.assertEqual('value is not optional, but was null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(int).validate('bibo')
        self.assertEqual("value is expected to have type 'int', but was type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(int, choices=[7, 11, 13, 17, 19]).validate(18)
        self.assertEqual("value is expected to be one of [7, 11, 13, 17, 19], but was 18",
                         f'{cm.exception}')

    def test_list(self):
        self.assertIsNone(TypeDef(list, optional=True).validate(None))
        self.assertIsNone(TypeDef(list).validate([]))
        self.assertIsNone(TypeDef(list).validate([1, 2, 3, 'A', 'B']))
        self.assertIsNone(TypeDef(list, item_type=TypeDef(int)).validate([1, 2, 3]))
        self.assertIsNone(TypeDef(list, item_type=TypeDef(str)).validate(['A', 'B']))
        self.assertIsNone(TypeDef(list, item_type=TypeDef(str, optional=True)).validate(['A', None, 'B']))

        with self.assertRaises(ValueError) as cm:
            TypeDef(list).validate(None)
        self.assertEqual('value is not optional, but was null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list).validate('bibo')
        self.assertEqual("value is expected to have type 'list', but was type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int)).validate([1, 2, 3, 'A', 'B'])
        self.assertEqual("index 3: value is expected to have type 'int', but was type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int)).validate([1, 2, None])
        self.assertEqual('index 2: value is not optional, but was null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int), num_items=3).validate([1, 2])
        self.assertEqual('number of items must be 3, but was 2',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int), num_items_min=3).validate([1, 2])
        self.assertEqual('number of items must not be less than 3, but was 2',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int), num_items_max=3).validate([1, 2, 3, 4])
        self.assertEqual('number of items must not be greater than 3, but was 4',
                         f'{cm.exception}')

    def test_dict(self):
        self.assertIsNone(TypeDef(dict, optional=True).validate(None))
        self.assertIsNone(TypeDef(dict).validate({}))
        self.assertIsNone(TypeDef(dict).validate(dict(A=2, B='X')))
        self.assertIsNone(TypeDef(dict, item_type=TypeDef(int))
                          .validate(dict(A=2, B=3)))
        self.assertIsNone(TypeDef(dict, key_type=TypeDef(str))
                          .validate(dict(A=2, B='X')))
        self.assertIsNone(TypeDef(dict, key_type=TypeDef(str), item_type=TypeDef(int))
                          .validate(dict(A=2, B=3)))

    def test_object(self):
        self.assertIsNone(TypeDef(object, optional=True).validate(None))
        self.assertIsNone(TypeDef(object).validate({}))
        self.assertIsNone(TypeDef(object).validate(dict(A=2, B='X')))
        self.assertIsNone(TypeDef(object, properties=[PropertyDef('A', TypeDef(int)),
                                                      PropertyDef('B', TypeDef(str))]).validate(dict(A=2, B='X')))

        with self.assertRaises(ValueError) as cm:
            TypeDef(object).validate(None)
        self.assertEqual('value is not optional, but was null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(object).validate('bibo')
        self.assertEqual("value is expected to have type 'dict', but was type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(object, properties=[PropertyDef('A', TypeDef(int)),
                                        PropertyDef('B', TypeDef(str))]).validate(dict(A=1, B=2))
        self.assertEqual("property 'B': value is expected to have type 'str', but was type 'int'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(object, properties=[PropertyDef('A', TypeDef(int)),
                                        PropertyDef('B', TypeDef(str))]).validate(dict(A=1, B='X', C=True))
        self.assertEqual("unexpected property 'C' found",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(object, properties=[PropertyDef('A', TypeDef(int)),
                                        PropertyDef('B', TypeDef(str))]).validate(dict(A=1, B='X', X=1.5, Y=9.1))
        self.assertEqual("unexpected properties found: ['X', 'Y']",
                         f'{cm.exception}')

    def test_object_in_list_in_object(self):
        with self.assertRaises(ValueError) as cm:
            TypeDef(object, properties=[PropertyDef('A', TypeDef(int)),
                                        PropertyDef('B',
                                                    TypeDef(list, item_type=TypeDef(object, properties=[
                                                        PropertyDef('X', TypeDef(float)),
                                                        PropertyDef('Y', TypeDef(float)),
                                                    ])))]).validate(dict(A=1,
                                                                         B=[dict(X=1.2, Y=5.2),
                                                                            dict(X=2.3, Y=-4.8),
                                                                            dict(X=2.3, Y='6.4')]))
        self.assertEqual("property 'B': index 2: property 'Y': "
                         "value is expected to have type 'float', but was type 'str'",
                         f'{cm.exception}')
