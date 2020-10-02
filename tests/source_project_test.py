import os
import time
import unittest
from pathlib import Path

import cwbar.source_project
import cwbar.settings

cwbar.settings.BASE_SOURCES = os.path.abspath(os.path.join("data", "sources"))


class SourceProjectTest(unittest.TestCase):

    def test_source_project_get_project(self):
        project = cwbar.source_project.SourceProject.get_project("project-a")
        self.assertEqual(project.name, "project-a")

    def test_source_project_get_dependencies(self):
        project = cwbar.source_project.SourceProject.get_project("project-c")
        self.assertEqual(2, len(project.get_dependencies()))

    def test_source_project_dependencies_to_build(self):
        project = cwbar.source_project.SourceProject.get_project("project-c")
        self.assertEqual(2, len(project.get_dependencies()))

    def test_source_project_get_changed_poms(self):
        project = cwbar.source_project.SourceProject.get_project("project-c")
        pom = os.path.join(project.get_source_dir(), "pom.xml")
        time.sleep(1)
        Path(pom).touch(mode=0o777, exist_ok=True)
        self.assertIn(os.path.relpath(pom, project.get_source_dir()), project.get_changed_poms())

    def test_source_project_build(self):
        project = cwbar.source_project.SourceProject.get_project("project-c")
        self.assertEqual(project.build_with_dependencies(False, False, False), True)

    def test_source_project_build_quick(self):
        project = cwbar.source_project.SourceProject.get_project("project-c")
        pom = os.path.join(project.get_source_dir(), "pom.xml")
        time.sleep(1)
        Path(pom).touch(mode=0o777, exist_ok=True)
        self.assertEqual(project.build_quick(False, False), True)

    def test_source_project_get_distributions(self):
        project = cwbar.source_project.SourceProject.get_project("project-d")
        self.assertEqual(list(project.get_distribution_projects(False)), ["d/distribution/application/pom.xml"])
        self.assertEqual(list(project.get_distribution_projects(True)), ["d/distribution/application/pom.xml",
                                                                         "d/distribution/main/pom.xml"])


if __name__ == '__main__':
    unittest.main()
