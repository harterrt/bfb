import json
import os

default_path = '~/.config/bfb.conf'

class Config(object):
    def __init__(self, path = default_path):
        self.path = os.path.expanduser(path)

        if not os.path.isfile(self.path):
            self.contents = {}
        else:
            with open(self.path, 'r') as config_file:
                self.contents = json.loads(config_file.read())

    def save(self):
        with open(self.path, 'w') as conf_file:
            conf_file.write(json.dumps(self.contents))
