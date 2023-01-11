import os


class SourceProjectConfig:

    def __init__(self, project_dir):
        self.ignored_dirs = []
        self.dist_pattern = []
        self.load(os.path.join(project_dir, ".cwproject"))

    def load(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                exec(f.read(), self.__dict__)

