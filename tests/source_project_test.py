import os
import time
import unittest
from pathlib import Path

from cwbar.source_project import SourceProject
import cwbar.settings as settings

settings.BASE_SOURCES = os.path.abspath(os.path.join("data", "sources"))


class SourceProjectTest(unittest.TestCase):

    def test_source_project_get_project(self):
        project = SourceProject.get_project("project-a")
        self.assertEqual(project.name, "project-a")

    def test_source_project_get_dependencies(self):
        project = SourceProject.get_project("project-c")
        self.assertEqual(2, len(project.get_dependencies()))

    def test_source_project_get_changed_poms(self):
        project = SourceProject.get_project("project-c")
        pom = os.path.join(project.get_source_dir(), "pom.xml")
        time.sleep(1)
        Path(pom).touch(mode=0o777, exist_ok=True)
        self.assertIn(os.path.relpath(pom, project.get_source_dir()), project.get_changed_poms(False))

    def test_source_project_build(self):
        project = SourceProject.get_project("project-c")
        self.assertEqual(project.build_with_dependencies(False, False), None)

    def test_source_project_build_quick(self):
        project = SourceProject.get_project("project-c")
        pom = os.path.join(project.get_source_dir(), "pom.xml")
        time.sleep(1)
        Path(pom).touch(mode=0o777, exist_ok=True)
        self.assertEqual(project.build_quick(False, False), True)


if __name__ == '__main__':
    unittest.main()
