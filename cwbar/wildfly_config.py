import datetime
import os
import shutil

from lxml import etree


class DataSourceConfig:
    def __init__(self, node):
        self.node = node

    def get_name(self):
        return self.node.get("jndi-name")

    def get_connection(self):
        return self.node.find("{*}connection-url").text

    def set_connection(self, value):
        self.node.find("{*}connection-url").text = value

    def get_user(self):
        return self.node.find("{*}security/{*}user-name").text

    def set_user(self, value):
        self.node.find("{*}security/{*}user-name").text = value

    def get_password(self):
        return self.node.find("{*}security/{*}password").text

    def set_password(self, value):
        self.node.find("{*}security/{*}password").text = value

    def get_driver(self):
        return self.node.find("{*}driver").text

    def set_driver(self, value):
        self.node.find("{*}driver").text = value


class WildflyConfig:

    def __init__(self, server_name, file_name):
        self.server_name = server_name
        self.file_name = file_name
        self.tree = etree.parse(file_name)

    def get_data_sources(self):
        for node in self.tree.getroot().findall("{*}profile/{*}subsystem/{*}datasources/{*}datasource"):
             yield DataSourceConfig(node)

    def backup(self):
        backup_dir = os.path.expanduser(os.path.join("~", ".cwasp", "control", "servers", self.server_name, "backup"))
        os.makedirs(backup_dir, exist_ok=True)
        print(self.file_name)
        backup_file_name = os.path.basename(self.file_name) + datetime.datetime.now().isoformat()
        shutil.copy(self.file_name, os.path.join(backup_dir, backup_file_name))

    def save(self):
        self.backup()
        self.tree.write(self.file_name, xml_declaration=True, encoding="utf-8")

