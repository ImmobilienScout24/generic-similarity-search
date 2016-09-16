from pybuilder.core import init, use_plugin
import os

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")
use_plugin("python.coverage")
use_plugin('exec')
use_plugin('copy_resources')
use_plugin('filter_resources')


def get_version():
    version_from_env = os.environ.get("version")
    return version_from_env if version_from_env else '0.0.0-SNAPSHOT'


default_task = ['clean', 'analyze', 'package']
version = get_version()
name = "generic_similarity_search"


@init
def initialize(project):
    print("initialize project")
    project.build_depends_on("unittest2")
    project.build_depends_on("mock")

    project.depends_on('numpy')
    project.depends_on('pyflann')
    project.depends_on('boto3')
    project.depends_on('pyproj')
    project.depends_on('tornado')
    project.depends_on('dyject')
    project.depends_on('checksumdir')

    project.get_property('filter_resources_glob').extend(['**/generic_similarity_search/__init__.py'])

    project.set_property('copy_resources_target', '$dir_dist')
    project.set_property('analyze_command', 'if [ -d .git/hooks/ ]; then ln -fs ../../git-hooks/pre-push .git/hooks/pre-push; fi')
    project.set_property('coverage_break_build', False)
    project.set_property('install_dependencies_upgrade', True)
    project.set_property('analyze_propagate_stdout', True)
    project.set_property('analyze_propagate_stderr', True)
    project.set_property('install_dependencies_index_url', "https://ppp.rz.is:5000/dev/dev/+simple/")


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    print("initialize project for teamcity")
    project.default_task = [
        'clean',
        'install_dependencies',
        'publish'
    ]
