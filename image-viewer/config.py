import json

CONFIG_PATH = "configs/"
CONFIG1 = "config1.json"
CONFIG2 = "config2.json"
BASE_CONFIG = "base_config.json"

class Config(dict):
    def __init__(self, config=CONFIG_PATH+CONFIG1, base_config=CONFIG_PATH+BASE_CONFIG):
        self.config_path = config
        with open(self.config_path, 'r') as f1, open(base_config, 'r') as f2:
            self.config_json = json.load(f1)
            self.base_config_json = json.load(f2)
            self.complete_json = {**self.base_config_json, **self.config_json}
            self.complete_json['actions'] = {**self.base_config_json['actions'], **self.config_json['actions']}
        pass

    def _update(self):
        with open(self.config_path, 'w+') as f:
            f.write(str(self.config_json).replace("'", '"'))

    def put(self, key, value=None):
        self.config_json[key] = value
        self._update()
        pass

    def delete(self, key):
        del self.config_json[key]
        self._update()
        pass

    def __setitem__(self, b, c):
        self.complete_json[b] = c

    def __getitem__(self, b):
        return self.complete_json[b]

    def __iter__(self):
        return self.complete_json.__iter__()


def createConfig():
    try:
        config = Config()
        return config
    except (FileNotFoundError, PermissionError) as e:
        print(e)
        return None
