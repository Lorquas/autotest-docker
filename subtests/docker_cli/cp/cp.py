"""
Test output of the docker cp command

1. Look for an image or container
2. Run the docker cp command on it
3. Make sure the file was successfully copied
"""

# Okay to be less-strict for these cautions/warnings in subtests
# pylint: disable=C0103,C0111,R0904,C0103

from autotest.client import utils
from dockertest import subtest
from dockertest import xceptions
from dockertest.dockercmd import NoFailDockerCmd
import filecmp
import os
import random


class cp(subtest.Subtest):
    config_section = 'docker_cli/cp'

    def run_once(self):
        super(cp, self).run_once()
        cpfile = self.config['basic_file']
        container = self._find_container_with_file(cpfile)
        tempdir = utils.run("mktemp -d").stdout.strip() + "/"
        #build arg list and execute command
        subargs = [container + ":" + cpfile]
        subargs.append(tempdir)
        nfdc = NoFailDockerCmd(self, "cp", subargs,
                               timeout=self.config['docker_timeout'])
        nfdc.execute()
        #save instance vars for later
        self.stuff['tempdir'] = tempdir
        file_path = self._target_path(cpfile, container)
        self.stuff['file_path'] = file_path
        copied_path = tempdir + cpfile.split('/')[-1]
        self.stuff['copied_path'] = copied_path

    def _target_path(self, target_file,
                    container,
                    docker_root='/var/lib/docker/'):
        return docker_root + 'containers/' + container + '/root' + target_file

    def _find_container_with_file(self, target_file,
                                 docker_root='/var/lib/docker/'):
        #finda all containers
        containers = os.walk(docker_root + 'containers/').next()[1]
        #look for containers containing desired file
        isfile = lambda x: os.path.isfile(self._target_path(target_file, x))
        containers = filter(isfile, containers)
        if not containers:
            raise xceptions.DockerTestNAError("No containers with "
                                              "viable filesystems found.")
        return random.choice(containers)

    def postprocess(self):
        self.verify_files_identical(self.stuff['file_path'],
                                    self.stuff['copied_path'])

    def verify_files_identical(self, docker_file, copied_file):
        self.failif(not filecmp.cmp(docker_file, copied_file),
                    "Copied file '%s' does not match docker file "
                    "'%s'." % (copied_file, docker_file))
        self.loginfo("Copied file matches docker file.")

    def cleanup(self):
        if self.config['remove_after_test'] and self.stuff['tempdir']:
            utils.run("rm -rf " + self.stuff['tempdir'])

