import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from ragflow_knowledge_mcp_server.utils import get_str_property, get_int_property, get_float_property, get_bool_property


class TestGetStrProperty(unittest.TestCase):
    def test_get_from_props(self):
        """Test retrieving a string property directly from the properties dictionary."""
        props = {'key': 'value'}
        self.assertEqual(get_str_property(props, 'key'), 'value')

    def test_get_from_props_with_conversion(self):
        """Test that a non-string value from props is converted to a string."""
        props = {'key': 123}
        self.assertEqual(get_str_property(props, 'key'), '123')

    def test_get_from_props_with_whitespace(self):
        """Test that a value with leading/trailing whitespace is handled correctly."""
        props = {'key': '  value  '}
        self.assertEqual(get_str_property(props, 'key'), '  value  ')

    def test_get_from_props_blank_value_fallback_to_default(self):
        """Test fallback to default value when prop value is blank."""
        props = {'key': '   '}
        self.assertEqual(get_str_property(props, 'key', default_value='default'), 'default')

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'env_value'})
    def test_get_from_env_var(self):
        """Test retrieving a property from an environment variable when not in props."""
        props = {}
        self.assertEqual(get_str_property(props, 'key', env_var_name='TEST_ENV_VAR'), 'env_value')

    @patch.dict(os.environ, {'TEST_ENV_VAR': '  env_value_with_space  '})
    def test_get_from_env_var_with_whitespace(self):
        """Test that env var value with whitespace is returned as is."""
        props = {}
        self.assertEqual(get_str_property(props, 'key', env_var_name='TEST_ENV_VAR'), '  env_value_with_space  ')

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'env_value'})
    def test_props_take_precedence_over_env_var(self):
        """Test that the properties dictionary value is used even if an environment variable is set."""
        props = {'key': 'prop_value'}
        self.assertEqual(get_str_property(props, 'key', env_var_name='TEST_ENV_VAR'), 'prop_value')

    def test_get_default_value(self):
        """Test that the default value is returned when the property is not in props or env vars."""
        props = {}
        self.assertEqual(get_str_property(props, 'key', default_value='default'), 'default')

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'env_value'})
    def test_env_var_takes_precedence_over_default(self):
        """Test that the environment variable is used even if a default value is provided."""
        props = {}
        self.assertEqual(get_str_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value='default'),
                         'env_value')

    def test_return_none_when_not_found(self):
        """Test that None is returned when the property is not found and no default is provided."""
        props = {}
        self.assertIsNone(get_str_property(props, 'key'))

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'env_value'})
    def test_fallback_from_blank_props_to_env_var(self):
        """Test fallback to environment variable when the properties dictionary value is blank."""
        props = {'key': '   '}
        self.assertEqual(get_str_property(props, 'key', env_var_name='TEST_ENV_VAR'), 'env_value')

    def test_fallback_from_blank_props_and_env_to_default(self):
        """Test fallback to default value when both props and env var are blank."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': '   '}):
            props = {'key': '   '}
            self.assertEqual(get_str_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value='default'),
                             'default')

    def test_invalid_env_var_name(self):
        """Test that a blank or invalid environment variable name is ignored."""
        props = {}
        self.assertEqual(get_str_property(props, 'key', env_var_name='  ', default_value='default'), 'default')
        self.assertIsNone(get_str_property(props, 'key', env_var_name='  '))


class TestGetIntProperty(unittest.TestCase):
    def test_get_from_props_as_int(self):
        """Test retrieving an integer property directly from the properties dictionary."""
        props = {'key': 123}
        self.assertEqual(get_int_property(props, 'key'), 123)

    def test_get_from_props_as_string(self):
        """Test retrieving an integer from a string value in the properties dictionary."""
        props = {'key': '456'}
        self.assertEqual(get_int_property(props, 'key'), 456)

    def test_get_from_props_with_whitespace(self):
        """Test retrieving an integer from a string with whitespace."""
        props = {'key': '  789  '}
        self.assertEqual(get_int_property(props, 'key'), 789)

    def test_get_from_props_invalid_string(self):
        """Test that an invalid integer string in props falls back to default."""
        props = {'key': 'abc'}
        self.assertEqual(get_int_property(props, 'key', default_value=0), 0)

    @patch.dict(os.environ, {'TEST_ENV_VAR': '123'})
    def test_get_from_env_var(self):
        """Test retrieving an integer from an environment variable."""
        props = {}
        self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR'), 123)

    @patch.dict(os.environ, {'TEST_ENV_VAR': '  456  '})
    def test_get_from_env_var_with_whitespace(self):
        """Test retrieving an integer from an environment variable with whitespace."""
        props = {}
        self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR'), 456)

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'abc'})
    def test_get_from_env_var_invalid_string(self):
        """Test that an invalid integer string in env var falls back to default."""
        props = {}
        self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=0), 0)

    def test_get_default_value(self):
        """Test that the default value is returned when the property is not found."""
        props = {}
        self.assertEqual(get_int_property(props, 'key', default_value=789), 789)

    def test_return_none_when_not_found(self):
        """Test that None is returned when the property is not found and no default is provided."""
        props = {}
        self.assertIsNone(get_int_property(props, 'key'))

    @patch.dict(os.environ, {'TEST_ENV_VAR': '123'})
    def test_props_take_precedence(self):
        """Test that props value takes precedence over environment variable."""
        props = {'key': 999}
        self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR'), 999)

    @patch.dict(os.environ, {'TEST_ENV_VAR': '123'})
    def test_env_var_takes_precedence_over_default(self):
        """Test that environment variable takes precedence over default value."""
        props = {}
        self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=0), 123)

    def test_fallback_from_invalid_props_to_env(self):
        """Test fallback to environment variable when props value is invalid."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': '123'}):
            props = {'key': 'abc'}
            self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR'), 123)

    def test_fallback_to_default_with_invalid_props_and_env(self):
        """Test fallback to default when both props and env var are invalid."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': 'abc'}):
            props = {'key': 'xyz'}
            self.assertEqual(get_int_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=0), 0)


class TestGetFloatProperty(unittest.TestCase):
    def test_get_from_props_as_float(self):
        """Test retrieving a float property directly from the properties dictionary."""
        props = {'key': 123.45}
        self.assertAlmostEqual(get_float_property(props, 'key'), 123.45)

    def test_get_from_props_as_string(self):
        """Test retrieving a float from a string value in the properties dictionary."""
        props = {'key': '456.78'}
        self.assertAlmostEqual(get_float_property(props, 'key'), 456.78)

    def test_get_from_props_with_whitespace(self):
        """Test retrieving a float from a string with whitespace."""
        props = {'key': '  789.01  '}
        self.assertAlmostEqual(get_float_property(props, 'key'), 789.01)

    def test_get_from_props_invalid_string(self):
        """Test that an invalid float string in props falls back to default."""
        props = {'key': 'abc'}
        self.assertAlmostEqual(get_float_property(props, 'key', default_value=0.0), 0.0)

    @patch.dict(os.environ, {'TEST_ENV_VAR': '123.45'})
    def test_get_from_env_var(self):
        """Test retrieving a float from an environment variable."""
        props = {}
        self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR'), 123.45)

    @patch.dict(os.environ, {'TEST_ENV_VAR': '  456.78  '})
    def test_get_from_env_var_with_whitespace(self):
        """Test retrieving a float from an environment variable with whitespace."""
        props = {}
        self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR'), 456.78)

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'abc'})
    def test_get_from_env_var_invalid_string(self):
        """Test that an invalid float string in env var falls back to default."""
        props = {}
        self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=0.0), 0.0)

    def test_get_default_value(self):
        """Test that the default value is returned when the property is not found."""
        props = {}
        self.assertAlmostEqual(get_float_property(props, 'key', default_value=789.01), 789.01)

    def test_return_none_when_not_found(self):
        """Test that None is returned when the property is not found and no default is provided."""
        props = {}
        self.assertIsNone(get_float_property(props, 'key'))

    @patch.dict(os.environ, {'TEST_ENV_VAR': '123.45'})
    def test_props_take_precedence(self):
        """Test that props value takes precedence over environment variable."""
        props = {'key': 999.99}
        self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR'), 999.99)

    @patch.dict(os.environ, {'TEST_ENV_VAR': '123.45'})
    def test_env_var_takes_precedence_over_default(self):
        """Test that environment variable takes precedence over default value."""
        props = {}
        self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=0.0), 123.45)

    def test_fallback_from_invalid_props_to_env(self):
        """Test fallback to environment variable when props value is invalid."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': '123.45'}):
            props = {'key': 'abc'}
            self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR'), 123.45)

    def test_fallback_to_default_with_invalid_props_and_env(self):
        """Test fallback to default when both props and env var are invalid."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': 'abc'}):
            props = {'key': 'xyz'}
            self.assertAlmostEqual(get_float_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=0.0),
                                   0.0)


class TestGetBoolProperty(unittest.TestCase):
    def test_get_from_props_as_bool(self):
        """Test retrieving a boolean property directly from the properties dictionary."""
        props = {'key': True}
        self.assertTrue(get_bool_property(props, 'key'))
        props = {'key': False}
        self.assertFalse(get_bool_property(props, 'key'))

    def test_get_from_props_as_string_true(self):
        """Test retrieving a boolean from various 'true' string values in props."""
        for val in ['true', 'yes', '1', 'y', 'on', ' True ', ' YES ']:
            with self.subTest(val=val):
                props = {'key': val}
                self.assertTrue(get_bool_property(props, 'key'))

    def test_get_from_props_as_string_false(self):
        """Test retrieving a boolean from various 'false' string values in props."""
        for val in ['false', 'no', '0', 'n', 'off', ' False ', ' NO ']:
            with self.subTest(val=val):
                props = {'key': val}
                self.assertFalse(get_bool_property(props, 'key'))

    def test_get_from_props_as_int(self):
        """Test retrieving a boolean from an integer value in props."""
        props = {'key': 1}
        self.assertTrue(get_bool_property(props, 'key'))
        props = {'key': 0}
        self.assertFalse(get_bool_property(props, 'key'))

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'true'})
    def test_get_from_env_var(self):
        """Test retrieving a boolean from an environment variable."""
        props = {}
        self.assertTrue(get_bool_property(props, 'key', env_var_name='TEST_ENV_VAR'))

    def test_get_default_value(self):
        """Test that the default value is returned when the property is not found."""
        props = {}
        self.assertTrue(get_bool_property(props, 'key', default_value=True))
        self.assertFalse(get_bool_property(props, 'key', default_value=False))

    def test_return_none_when_not_found(self):
        """Test that None is returned when the property is not found and no default is provided."""
        props = {}
        self.assertIsNone(get_bool_property(props, 'key'))

    @patch.dict(os.environ, {'TEST_ENV_VAR': 'true'})
    def test_props_take_precedence(self):
        """Test that props value takes precedence over environment variable."""
        props = {'key': False}
        self.assertFalse(get_bool_property(props, 'key', env_var_name='TEST_ENV_VAR'))

    def test_fallback_from_invalid_props_to_env(self):
        """Test fallback to environment variable when props value is invalid."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': 'yes'}):
            props = {'key': 'invalid'}
            self.assertTrue(get_bool_property(props, 'key', env_var_name='TEST_ENV_VAR'))

    def test_fallback_to_default_with_invalid_props_and_env(self):
        """Test fallback to default when both props and env var are invalid."""
        with patch.dict(os.environ, {'TEST_ENV_VAR': 'invalid'}):
            props = {'key': 'invalid'}
            self.assertTrue(get_bool_property(props, 'key', env_var_name='TEST_ENV_VAR', default_value=True))


if __name__ == '__main__':
    unittest.main()
