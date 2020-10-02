import glob
import os
import re
import pathlib

import cwbar.cmd
import cwbar.settings


class SourceProject:
    projects = {}

    @staticmethod
    def get_project(name, context=None):
        full_name = context + "-" + name if context else name
        project = SourceProject.projects.get(full_name) or SourceProject(name, context)
        SourceProject.projects[full_name] = project
        return project

    def __init__(self, name, context):
        self.name = name
        self.context = context
        self.dependencies = self.calc_dependencies()

    def __repr__(self):
        return "SourceProject(" + self.name + ((", " + self.context + ")") if self.context else ")")

    def calc_dependencies(self):
        dependencies = set()
        with open(self.get_pom(), "r") as f:
            for line in f:
                m = re.match("<(.*)[-.]version>.*-SNAPSHOT</.*[-.]version>", line.strip())
                if m:
                    dependencies.add(SourceProject.get_project(m.group(1), self.context if self.context else self.name))
        return dependencies

    def get_dependencies(self):
        return set(self.dependencies)

    def dependencies_to_build(self):
        all_dependencies = []
        for dependency in self.get_dependencies():
            all_dependencies = dependency.dependencies_to_build() + [dependency] + all_dependencies
        seen = set()
        return [x for x in all_dependencies if not (x in seen or seen.add(x))]

    def mvn(self, pom, args):
        cwbar.cmd.execute(os.path.expanduser(cwbar.settings.MVN) + " -q -T1.0C -f " + pom + " " + args)

    def build(self, only_this, clean, quick, full_distribution):
        if only_this:
            self.build_only_this(clean, quick, full_distribution, True)
        else:
            self.build_with_dependencies(clean, quick, full_distribution)

    def build_only_this(self, clean, quick, full_distribution, force_add_distribution):
        if quick:
            return self.build_quick(clean, full_distribution, force_add_distribution)
        else:
            self.mvn(self.get_pom(), (" clean " if clean else "") + "install")
            self.touch_marker()
            return True

    def build_with_dependencies(self, clean, quick, full_distribution):
        dependencies_to_build = self.dependencies_to_build()
        print("With dependencies " + str(dependencies_to_build))
        force_add_distribution = False
        for dependency in dependencies_to_build:
            force_add_distribution = dependency.build_only_this(clean, quick, full_distribution, False) or \
                                     force_add_distribution
        return self.build_only_this(clean, quick, full_distribution, force_add_distribution)

    def build_compound(self, clean, full_distribution):
        pom = self.get_compound_pom()
        distribution_projects = map(lambda x: os.path.join(self.name, x),
                                    self.get_distribution_projects(full_distribution))
        self.mvn(pom, "-pl " + ",".join(distribution_projects) + " -am " + (
            " clean " if clean else "") + "package")
        self.touch_marker()

    def build_quick(self, clean, force_add_distribution=False, full_distribution=False):
        changed_poms = self.get_changed_poms()
        distribution_poms = set(self.get_distribution_projects(full_distribution))
        step_one_poms = changed_poms - distribution_poms
        # distribution собираем отдельно ибо при одновременных изменениях в транзитивных зависимостях порядок сборки
        # не может быть полнценно вычислен при частичной сборке и в distribution может быть включена старая версия из
        # ~/.m2
        step_two_poms = distribution_poms if force_add_distribution else changed_poms & distribution_poms
        if step_one_poms or step_two_poms:
            if step_one_poms:
                self.mvn(self.get_pom(), "-pl " + ",".join(step_one_poms) + (" clean " if clean else "") + " install")
            if step_two_poms:
                self.mvn(self.get_pom(), "-pl " + ",".join(step_two_poms) + (" clean " if clean else "") + " install")
            self.touch_marker()
            return True
        else:
            print(self.name + " - NO CHANGE!!!")
            self.touch_marker()
            return False

    def get_source_dir(self):
        if self.context:
            full_name = self.context + "-" + self.name
            full_name = os.path.expanduser(os.path.join(cwbar.settings.BASE_SOURCES, full_name))
            if os.path.exists(full_name):
                return full_name
        return os.path.expanduser(os.path.join(cwbar.settings.BASE_SOURCES, self.name))

    def get_pom(self):
        return os.path.join(self.get_source_dir(), "pom.xml")

    def get_compound_pom(self):
        return self.get_source_dir() + "-pom.xml"

    @staticmethod
    def is_distribution_pom(pom):
        with open(pom) as f:
            data = f.read()
            return "<packaging>ear" in data or "<packaging>war" in data

    def get_distribution_projects(self, full_distribution):
        minimum_set = {"application", "middleware", "login", "api"}
        pattern = os.path.join(self.get_source_dir(), "*", "distribution*", "**", "pom.xml")
        for pom in glob.glob(pattern, recursive=True):
            pom_dir = os.path.basename(os.path.dirname(pom))
            if self.is_distribution_pom(pom) and pom_dir != "testing" and (full_distribution or pom_dir in minimum_set):
                yield pom[len(self.get_source_dir()) + 1:]

    def get_ignored_dirs(self):
        if self.name == "core":
            return ["core/reloadable/tests/it",
                    "core/codegen/tests",
                    "core/tests",
                    "core/testing/engine",
                    "core/testing/testing-gui",
                    "core/testing/model-ddl-test",
                    "core/testing/jmeter-plugin",
                    "core/dataaccess/unientity-support-web",
                    "core/dataaccess/unientity-support",
                    "core/license-manager",
                    "core/gui/web/header-component-plugin-frontend",
                    "core/gui/web/application-styles-frontend",
                    "core/dsign/webservice-csp",
                    "tools/.*",
                    "core/security/it",
                    "core/proxy/.*"]
        elif self.name == "nsi":
            return ["regulatoryinfo/distributions/final/it"]
        elif self.name == "docreg":
            return ["docregistries/gov-tasks-integration/gov-tasks-integration-it"]
        elif self.name == "retools":
            return ["retools-reporting/retools-reporting-profile"]
        elif self.name == "fileserver":
            return ["selenium-tests"]
        elif self.name == "fkc":
            return ["fkc-it", "fkc/integration/puot-client"]
        else:
            return []

    def get_changed_poms(self):
        changed_files = self.get_changed_files()
        changed_dirs = set(map(lambda cf: os.path.dirname(cf), changed_files))
        return set(map(lambda cd: os.path.relpath(self.get_pom_by_dir(cd), self.get_source_dir()), changed_dirs))

    def get_pom_by_dir(self, dir_name):
        while dir_name != self.get_source_dir():
            if os.path.exists(os.path.join(dir_name, "pom.xml")):
                return os.path.join(dir_name, "pom.xml")
            dir_name = os.path.dirname(dir_name)
        return self.get_pom()

    def get_changed_files(self):
        common_ignored = ["*/.hg*", "*/target*", "*/node_modules/*"]
        project_ignored = list(map(lambda m: os.path.join(self.get_source_dir(), m), self.get_ignored_dirs()))
        ignored = list(map(lambda p: " -path '" + p + "'", common_ignored))
        ignored += ((["-regex '" + "\\|".join(project_ignored) + "'"]) if (len(project_ignored) > 0) else [])
        ignored = "\\(" + " -or ".join(ignored) + " \\)"
        source_dir = self.get_source_dir()
        touch_file = self.get_touch_marker_file()
        c = "find " + source_dir + " " + ignored + " -prune -o -type f"
        if os.path.exists(touch_file):
            c += " -newer " + touch_file
        c += " -print"
        return [f for f in cwbar.cmd.execute_with_output(c) if f]

    def get_touch_marker_file(self):
        config_dir = os.path.expanduser(os.path.join("~", ".config", "krista"))
        os.makedirs(config_dir, exist_ok=True)
        full_name = self.context + "-" + self.name if self.context else self.name
        return os.path.join(config_dir, full_name + ".touch")

    def touch_marker(self):
        touch_marker_file = self.get_touch_marker_file()
        pathlib.Path(touch_marker_file).touch(mode=0o777, exist_ok=True)

    def get_distribution_project_targets(self, full_distribution):
        distributions = self.get_distribution_projects(full_distribution)
        result = set()
        for distribution in distributions:
            target_dir = os.path.join(self.get_source_dir(), os.path.dirname(distribution), "target")
            target_files = glob.glob(os.path.join(target_dir, "*.war")) + glob.glob(os.path.join(target_dir, "*.ear"))
            if len(target_files) == 0:
                raise Exception("Проект " + distribution + " не собран")
            result += target_files
        return result
