"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import configparser


class Config:
    """Configuration manager that can be instantiated per client."""

    def __init__(self, config_file: str):
        """
        Initialize config from a specific config file.

        Args:
            config_file: Path to the config file
        """
        self.config_file = config_file
        self.cp = configparser.ConfigParser()
        self.cp.read(config_file)

    def get_bool(self, section: str, option: str, default: bool = False) -> bool:
        """Get a boolean value from config."""
        try:
            value = self.cp.get(section, option)
            if value.lower() in ("true", "t", "yes", "y", "1"):
                return True
            else:
                return False
        except Exception:
            print(f"Exception getting option {section=} {option=} from {self.config_file}")
            return default

    def get_str(self, section: str, option: str, default: str | None = None) -> str | None:
        """Get a string value from config."""
        try:
            value = self.cp.get(section, option)
            return value
        except Exception:
            print(f"Exception getting option {section=} {option=} from {self.config_file}")
            return default
