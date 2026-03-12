from typing import List
import os
import re
import setuptools
import setuptools.command.bdist_wheel
import setuptools.command.sdist
import sys


_ERROR_MESSAGE_FILENAME = "error-message.txt"


class SourceDistributionBuildCmd(setuptools.command.sdist.sdist):
    user_options = [
        *setuptools.command.sdist.sdist.user_options,
        ("project-name-override=", None, "value to replace the project name with"),
        ("project-version-override=", None, "value to replace the project version with"),
        ("pkg-build-error-msg=", None, "build error message that will be printed on wheel build"),
    ]

    def _generate_error_message_file(self, file: str) -> None:
        msg = (
            self.pkg_build_error_msg
            or (
                "The project you're installing does not support the version of Python"
                " that you are currently using ({python_version}).\n"
                "For more details on supported Python version, read the documentation of the project"
                " that declares this package ({dist_name}) in its dependencies."
            )
        ).format(python_version=sys.version.split(" ", 1)[0], dist_name=self.distribution.name)
        with open(file, "w", encoding="utf-8") as fp:
            fp.write("\n")
            fp.write(
                self.pkg_build_error_msg
                or "This project does not support the version of Python you are currently using.\n"
                "For more details, read the documentation of the project that uses this package ({dist_name}) in its dependencies."
            )
            fp.write("\n")

    def initialize_options(self) -> None:
        super().initialize_options()
        self.project_name_override = None
        self.project_version_override = None
        self.pkg_build_error_msg = None

    def make_release_tree(self, base_dir: str, files: List[str]) -> None:
        files = ["pyproject.toml", "_custom_build/backend.py"]
        super().make_release_tree(base_dir, files)

        file = os.path.join(base_dir, _ERROR_MESSAGE_FILENAME)
        self.execute(
            self._generate_error_message_file, (file,), "generating error message text file"
        )
        self.filelist.files.append(file)

        if not self.project_name_override:
            return

        pyproject_path = os.path.join(base_dir, "pyproject.toml")
        with open(pyproject_path, encoding="utf-8") as fp:
            pyproject_content = fp.read()

        new_content = re.sub(
            r'^name = ".+"$',
            f'name = "{self.project_name_override}"',
            pyproject_content,
            flags=re.MULTILINE,
        )
        with open(pyproject_path, "w", encoding="utf-8") as fp:
            fp.write(new_content)

    def run(self) -> None:
        if self.project_name_override:
            self.distribution.metadata.name = self.project_name_override
        if self.project_version_override:
            self.distribution.metadata.version = self.project_version_override
        super().run()


setuptools.setup(cmdclass={"sdist": SourceDistributionBuildCmd})
