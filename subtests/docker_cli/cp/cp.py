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
from dockertest.output import OutputGood
from dockertest.dockercmd import NoFailDockerCmd
import os

class cp(subtest.Subtest):
	config_section = 'docker_cli/cp'

	def run_once(self):
        super(info, self).run_once()
        container = find_container()
        subargs = [container_id + ":" + self.config['basic_file']]
        tempdir = utils.run("mktmp -d").stdout.strip() + "/"
        subargs.append(tempdir)
        nfdc = NoFailDockerCmd(self, "cp", subargs)
        nfdc.execute()
        file_path = find_container_fs() + self.config['basic_file']
        copied_path = tempdir + self.config['basic_file'].split('/')[-1]
        self.stuff['file_path'] = file_path
        self.stuff['copied_path'] = copied_path

    def find_container():
        pass

    def find_dontainer_fs(id, docker_root="/var/lib/docker/"):
        pass

    def postprocess(self):
        # Raise exception on Go Panic or usage help message
        outputgood = OutputGood(self.stuff['cmdresult'])
        info_map = self._build_table(outputgood.stdout_strip)
        #verify each element
        self.verify_pool_name(info_map['Pool Name'])
        self.verify_sizes(info_map['Data file'],
                         info_map['Data Space Used'],
                         info_map['Data Space Total'],
                         info_map['Metadata file'],
                         info_map['Metadata Space Used'],
                         info_map['Metadata Space Total'])
