"""simp-logger/src/simplogger/logger.py
A simple logger using `logging` module with configurable logging levels, log pattern, log file path, log file rotation, etc.
"""

import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from sys import stderr

# Set to keep track of configured loggers
_configured: set[str] = set()


def _get_bool_env(name: str, default: bool = False) -> bool:
    """Helper to get boolean from environment variable"""
    return os.getenv(name, str(default)).lower() in ("true", "1", "yes", "on")


def _get_int_env(name: str, default: int) -> int:
    """Helper to get integer from environment variable"""
    try:
        return int(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default


def get_logger(name: str = "root",
               log_file_enabled: bool = None,
               log_console_enabled: bool = None,
               log_level: str = None,
               log_file: str = None,
               log_pattern: str = None,
               rotation_type: str = None,
               max_bytes: int | None = None,
               backup_count: int | None = None,
               when: str = None,
               interval: int | None = None,
               clean_handlers: bool | None = None,
               ) -> logging.Logger:
    """Get or configure a logger with the specified configuration.
    Note, if logger is already existing, it will be returned without reconfiguration.

    Args:
        :param name:         Name of the logger (default: "root").
        :param log_file_enabled:    Whether logging to file is enabled (default: from SIMP_LOGGER_LOG_FILE_ENABLED env var or True).
        :param log_console_enabled: Whether logging to console is enabled (default: from SIMP_LOGGER_LOG_CONSOLE_ENABLED env var or True).
        :param log_level:           Logging level (default: from SIMP_LOGGER_LOG_LEVEL env var or INFO).
        :param log_file:            Log file path (default: from SIMP_LOGGER_LOG_FILE env var or ~/logs/simp-logger.log).
        :param log_pattern:         Log pattern (default: from SIMP_LOGGER_LOG_PATTERN env var or a standard pattern).
        :param rotation_type:       Type of rotation: 'size' or 'time' (default: from SIMP_LOGGER_LOG_ROTATION_TYPE env var or 'size').
        :param max_bytes:           Max bytes per log file before rotation (default: from SIMP_LOGGER_LOG_MAX_BYTES env var or 10MB).
        :param backup_count:        Number of backup files to keep (default: from SIMP_LOGGER_LOG_BACKUP_COUNT env var or 5).
        :param when:                When to rotate logs for TimedRotatingFileHandler (default: from SIMP_LOGGER_LOG_ROTATION_WHEN env var or 'midnight').
                                    Values for when:
                                    - 'S' - Seconds
                                    - 'M' - Minutes
                                    - 'H' - Hours
                                    - 'D' - Days
                                    - 'W0'-'W6' - Weekdays (0=Monday, 6=Sunday)
                                    - 'midnight' - Roll over at midnight
        :param interval:            Interval for rotation (default: from SIMP_LOGGER_LOG_ROTATION_INTERVAL env var or 1).
        :param clean_handlers:      Whether to clean existing handlers (default: from SIMP_LOGGER_LOG_CLEANUP_ENABLED env var or False).

    Returns:
        The configured logger instance.
    """

    # Return existing logger if already configured
    if name in _configured:
        return logging.getLogger(name)

    # Get configs from parameters or environment variables
    if log_file_enabled is None:
        log_file_enabled = _get_bool_env("SIMP_LOGGER_LOG_FILE_ENABLED", True)
    if not log_file_enabled:
        stderr.write(f"Warning: logging to file is disabled for logger '{name}'.\n")

    if log_console_enabled is None:
        log_console_enabled = _get_bool_env("SIMP_LOGGER_LOG_CONSOLE_ENABLED", True)
    if not log_console_enabled:
        stderr.write(f"Warning: logging to console is disabled for logger '{name}'.\n")

    # Early return if logging handlers are disabled
    if not log_file_enabled and not log_console_enabled:
        log = logging.getLogger(name)
        _configured.add(name)
        return log

    log_level_str = os.getenv("SIMP_LOGGER_LOG_LEVEL", "INFO").upper() if log_level is None else log_level.upper()
    log_level_value = getattr(logging, log_level_str, logging.INFO)

    # Get logger from logger manager
    log = logging.getLogger(name)

    # Cleanup existing handlers if enabled
    clean_handlers = clean_handlers if clean_handlers is None \
        else _get_bool_env("SIMP_LOGGER_LOG_CLEANUP_ENABLED", False)

    if clean_handlers and log.handlers:
        handlers_to_remove = log.handlers.copy()
        for handler in handlers_to_remove:
            stderr.write(f"Warning: Removing existing handler {handler} for logger '{name}'.\n")
            log.removeHandler(handler)

    log.setLevel(log_level_value)

    # Get log pattern from parameters or environment or default
    log_pattern = log_pattern if log_pattern and log_pattern.strip() \
        else os.getenv("SIMP_LOGGER_LOG_PATTERN", "%(asctime)s %(levelname)s [%(threadName)s]: %(message)s")

    # Get rotation configuration
    max_bytes = max_bytes if max_bytes is not None and max_bytes > 0 \
        else int(os.getenv("SIMP_LOGGER_LOG_MAX_BYTES", str(10 * 1024 * 1024)))
    backup_count = backup_count if backup_count is not None and backup_count > 0 \
        else int(os.getenv("SIMP_LOGGER_LOG_BACKUP_COUNT", "5"))
    rotation_type = rotation_type if rotation_type is not None \
        else os.getenv("SIMP_LOGGER_LOG_ROTATION_TYPE", "size").lower()
    when = when if when is not None else os.getenv("SIMP_LOGGER_LOG_ROTATION_WHEN", "midnight")
    interval = interval if interval is not None else _get_int_env("SIMP_LOGGER_LOG_ROTATION_INTERVAL", 1)

    formatter = logging.Formatter(log_pattern)

    if log_file_enabled:
        # Get log file from parameters or environment or default
        if not log_file or not log_file.strip():
            log_file = os.getenv("SIMP_LOGGER_LOG_FILE")
            if not log_file or not log_file.strip():
                user_home = pathlib.Path.home()
                log_dir = user_home / "logs"
                log_file = str(log_dir / "simp-logger.log")

        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)

        # Setup file handler based on rotation configuration
        if rotation_type == "size":
            file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        else:
            # time-based rotation
            file_handler = TimedRotatingFileHandler(log_file, when=when, interval=interval, backupCount=backup_count)

        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        log_msg = (
            f"Logging to file enabled. Name: {name}, Level: {log_level_str}, File: {log_file}, "
            f"Rotation: {rotation_type}-based, "
            f"{f'max_bytes: {max_bytes}, ' if rotation_type == 'size' else f'when: {when}, interval: {interval}, '}"
            f"backups: {backup_count}."
        )
        log.info(log_msg)
        stderr.write(log_msg + "\n")

    if log_console_enabled:
        console_handler = logging.StreamHandler(stderr)
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)

        console_msg = f"Logging to console enabled for {name}."
        log.info(console_msg)
        stderr.write(console_msg + "\n")

    _configured.add(name)
    return log
