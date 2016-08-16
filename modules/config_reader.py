class ConfigReader(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not ConfigReader.__instance:
            ConfigReader.__instance = object.__new__(cls, *args, **kwargs)
            return ConfigReader.__instance

    def __init__(self, config, path):
        try:
            config.read(path)
            self.user = config.get('MySQL', 'user')
            self.password = config.get('MySQL', 'password')
            self.host = config.get('MySQL', 'host')
            self.dbname = config.get('MySQL', 'dbname')
        except Exception as e:
            raise e
