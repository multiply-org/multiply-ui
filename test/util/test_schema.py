import unittest

from multiply_ui.util.schema import TypeDef, PropertyDef


class TypeDefTest(unittest.TestCase):
    def test_primitives(self):
        self.assertIsNone(TypeDef(str, optional=True).validate(None))
        self.assertIsNone(TypeDef(int).validate(234))
        self.assertIsNone(TypeDef(float).validate(1.234))
        self.assertIsNone(TypeDef(str).validate('bibo'))

        with self.assertRaises(ValueError) as cm:
            TypeDef(int).validate(None)
        self.assertEqual('value is not optional, but found null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(int).validate('bibo')
        self.assertEqual("value is expected to have type 'int', but found type 'str'",
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
        self.assertEqual('value is not optional, but found null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list).validate('bibo')
        self.assertEqual("value is expected to have type 'list', but found type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int)).validate([1, 2, 3, 'A', 'B'])
        self.assertEqual("index 3: value is expected to have type 'int', but found type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(list, item_type=TypeDef(int)).validate([1, 2, None])
        self.assertEqual('index 2: value is not optional, but found null',
                         f'{cm.exception}')

    def test_dict(self):
        self.assertIsNone(TypeDef(dict, optional=True).validate(None))
        self.assertIsNone(TypeDef(dict).validate({}))
        self.assertIsNone(TypeDef(dict).validate(dict(A=2, B='X')))
        self.assertIsNone(TypeDef(dict, properties=[PropertyDef('A', TypeDef(int)),
                                                    PropertyDef('B', TypeDef(str))]).validate(dict(A=2, B='X')))

        with self.assertRaises(ValueError) as cm:
            TypeDef(dict).validate(None)
        self.assertEqual('value is not optional, but found null',
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(dict).validate('bibo')
        self.assertEqual("value is expected to have type 'dict', but found type 'str'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(dict, properties=[PropertyDef('A', TypeDef(int)),
                                      PropertyDef('B', TypeDef(str))]).validate(dict(A=1, B=2))
        self.assertEqual("property 'B': value is expected to have type 'str', but found type 'int'",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(dict, properties=[PropertyDef('A', TypeDef(int)),
                                      PropertyDef('B', TypeDef(str))]).validate(dict(A=1, B='X', C=True))
        self.assertEqual("unexpected property 'C' found",
                         f'{cm.exception}')

        with self.assertRaises(ValueError) as cm:
            TypeDef(dict, properties=[PropertyDef('A', TypeDef(int)),
                                      PropertyDef('B', TypeDef(str))]).validate(dict(A=1, B='X', X=1.5, Y=9.1))
        self.assertEqual("unexpected properties found: ['X', 'Y']",
                         f'{cm.exception}')

    def test_dict_in_list_in_dict(self):
        with self.assertRaises(ValueError) as cm:
            TypeDef(dict, properties=[PropertyDef('A', TypeDef(int)),
                                      PropertyDef('B',
                                                  TypeDef(list, item_type=TypeDef(dict, properties=[
                                                      PropertyDef('X', TypeDef(float)),
                                                      PropertyDef('Y', TypeDef(float)),
                                                  ])))]).validate(dict(A=1,
                                                                       B=[dict(X=1.2, Y=5.2),
                                                                          dict(X=2.3, Y=-4.8),
                                                                          dict(X=2.3, Y='6.4')]))
        self.assertEqual("property 'B': index 2: property 'Y': "
                         "value is expected to have type 'float', but found type 'str'",
                         f'{cm.exception}')
