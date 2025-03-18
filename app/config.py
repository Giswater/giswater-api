import configparser

# Get from config/app.config
config_file = "app/config/app.config"
cp = configparser.ConfigParser()
cp.read(config_file)

config = cp

def get_bool(section: str, option: str, default: bool = False) -> bool:
    try:
        value = config.get(section, option)
        if value.lower() in ("true", "t", "yes", "y", "1"):
            return True
        else:
            return False
    except:
        print(f"Exception getting option {section=} {option=}")
        return default

def get_str(section: str, option: str, default: str | None = None) -> str | None:
    try:
        value = config.get(section, option)
        return value
    except:
        print(f"Exception getting option {section=} {option=}")
        return default
