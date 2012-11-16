import logging, os, datetime, re
from distutils import file_util

logger = logging.getLogger("nginx_config")

class NginxConfig():
    """
        Mechanism supposes that client_max_body_size is already configured in nginx config file.
        It can ONLY update existing value.
    """

    DEFAULT_CLIENT_MAX_BODY_SIZE = 100

    CLIENT_MAX_BODY_SIZE = "client_max_body_size"

    CLIENT_MAX_BODY_SIZE_REGEX = r"%s\s+([0-9])+M" % CLIENT_MAX_BODY_SIZE

    def __init__(self, nginx_config_file_dir, nginx_conf_file, make_backups=False):
        self.nginx_config_file_dir = nginx_config_file_dir
        self.nginx_conf_file = nginx_conf_file
        self.nginx_config_path = os.path.join(self.nginx_config_file_dir, self.nginx_conf_file)
        self.make_backups = make_backups

    def _read(self):
        f = open(self.nginx_config_path)
        config_file = [line for line in f.readlines()]
        f.close()
        return config_file

    def _write(self, nginx_conf):
        if self.make_backups:
            self._make_backup()

        fwrite = open(self.nginx_config_path, "w")
        for line in nginx_conf:
            fwrite.write(line)
        fwrite.close()

    def _make_backup(self):
        nginx_config_file_copy = self.nginx_conf_file + "_" + str(datetime.datetime.now()).replace(" ", "_")
        nginx_config_copy_path = os.path.join(self.nginx_config_file_dir, nginx_config_file_copy)
        file_util.copy_file(self.nginx_config_path, nginx_config_copy_path)

    def get_client_max_body_size(self):
        if not os.path.isfile(self.nginx_config_path):
            logger.warn("No nginx config file found in path %s. Returning default. " % self.nginx_config_path)
            return self.DEFAULT_CLIENT_MAX_BODY_SIZE

        config_file = self._read()
        lines = [line for line in config_file if self.CLIENT_MAX_BODY_SIZE in line]

        if len(lines) > 1:
            logger.warn("Found %s occurences of client_max_body_size in nginx conf. Returning first." % len(lines))

        if not len(lines):
            logger.warn("WARNING! client_max_body_size is not configured in nginx. Returning default.")
            return self.DEFAULT_CLIENT_MAX_BODY_SIZE

        return int(re.search(self.CLIENT_MAX_BODY_SIZE_REGEX, lines[0]).group(1))

    def set_client_max_body_size(self, size):
        if not os.path.isfile(self.nginx_config_path):
            logger.warn("No nginx config file found in path " + self.nginx_config_path)
            return False

        nginx_conf = self._read()
        for line in nginx_conf:
            loc = nginx_conf.index(line)
            nginx_conf[loc] = re.sub(self.CLIENT_MAX_BODY_SIZE_REGEX, "%s %sM" % (self.CLIENT_MAX_BODY_SIZE, size), line)

        self._write(nginx_conf)
        return True
