"""utils.py: This file contains utility functions."""


def get_str_property(props: dict, prop_name: str, env_var_name: str | None = None, default_value: str | None = None,
                     ) -> str | None:
    """Gets a string property from the property dictionary, environment variable, or default value.

    This function first tries to get the property from the property dictionary.
    If not found or blank, it tries to get it from an environment variable.
    If still not found or blank, it returns the default value.

    Args:
        :param props:         Dictionary containing properties.
        :param prop_name:     Name of the property to retrieve.
        :param env_var_name:  Environment variable name to check if the property isn't found in the dictionary.
        :param default_value: Default value to return if the property isn't found in the dictionary or environment.

    Returns:
        String property value, or None if not found and no default value provided.
    """

    value = props.get(prop_name, None)

    if value is not None:
        value_str = value if isinstance(value, str) else str(value)
        if value_str.strip():
            return value_str

    if env_var_name and env_var_name.strip():
        import os
        value = os.getenv(env_var_name)

        if value and value.strip():
            return value

    return default_value


def get_int_property(props: dict, prop_name: str, env_var_name: str | None = None, default_value: int | None = None,
                     ) -> int | None:
    """Gets an integer property from the property dictionary, environment variable, or default value.

    This function first tries to get the property from the property dictionary.
    If not found or invalid, it tries to get it from an environment variable.
    If still not found or invalid, it returns the default value.

    Args:
        :param props:         Dictionary containing properties.
        :param prop_name:     Name of the property to retrieve.
        :param env_var_name:  Environment variable name to check if the property isn't found in the dictionary.
        :param default_value: Default value to return if the property isn't found in the dictionary or environment.

    Returns:
        Integer property value, or None if not found and no default value provided.
    """

    value = props.get(prop_name, None)

    if isinstance(value, int):
        return value

    if value is not None:
        value_str = (value if isinstance(value, str) else str(value)).strip()
        if value_str:
            try:
                return int(value_str)
            except ValueError:
                pass

    if env_var_name and env_var_name.strip():
        import os
        value_str = os.getenv(env_var_name)

        if value_str and value_str.strip():
            try:
                return int(value_str.strip())
            except ValueError:
                pass

    return default_value


def get_float_property(props: dict, prop_name: str, env_var_name: str | None = None, default_value: float | None = None,
                       ) -> float | None:
    """Gets a float property from the property dictionary, environment variable, or default value.

    This function first tries to get the property from the property dictionary.
    If not found or invalid, it tries to get it from an environment variable.
    If still not found or invalid, it returns the default value.

    Args:
        :param props:         Dictionary containing properties.
        :param prop_name:     Name of the property to retrieve.
        :param env_var_name:  Environment variable name to check if the property isn't found in the dictionary.
        :param default_value: Default value to return if the property isn't found in the dictionary or environment.

    Returns:
        Float property value, or None if not found and no default value provided.
    """

    value = props.get(prop_name, None)

    if isinstance(value, float):
        return value

    if value is not None:
        value_str = (value if isinstance(value, str) else str(value)).strip()
        if value_str:
            try:
                return float(value_str)
            except ValueError:
                pass

    if env_var_name and env_var_name.strip():
        import os
        value_str = os.getenv(env_var_name)

        if value_str and value_str.strip():
            try:
                return float(value_str.strip())
            except ValueError:
                pass

    return default_value


def get_bool_property(props: dict, prop_name: str, env_var_name: str | None = None, default_value: bool | None = None,
                      ) -> bool | None:
    """Gets a boolean property from the property dictionary, environment variable, or default value.

    This function first tries to get the property from the property dictionary.
    If not found or invalid, it tries to get it from an environment variable.
    If still not found or invalid, it returns the default value.

    Args:
        :param props:         Dictionary containing properties.
        :param prop_name:     Name of the property to retrieve.
        :param env_var_name:  Environment variable name to check if the property isn't found in the dictionary.
        :param default_value: Default value to return if the property isn't found in the dictionary or environment.

    Returns:
        Boolean property value, or None if not found and no default value provided.
    """

    value = props.get(prop_name, None)

    if isinstance(value, bool):
        return value

    if value is not None:
        if isinstance(value, str):
            value_str = value.strip().lower()
            if value_str in ['true', 'yes', '1', 'y', 'on']:
                return True
            elif value_str in ['false', 'no', '0', 'n', 'off']:
                return False
        elif isinstance(value, (int, float)):
            return bool(value)

    if env_var_name and env_var_name.strip():
        import os
        env_value = os.getenv(env_var_name)

        if env_value is not None:
            env_value = env_value.strip().lower()
            if env_value in ['true', 'yes', '1', 'y', 'on']:
                return True
            elif env_value in ['false', 'no', '0', 'n', 'off']:
                return False

    return default_value
