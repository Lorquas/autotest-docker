"""
This module provides helper classes that allow the testware
to connect to external tools and trackers such as bugzilla.
"""

# Pylint runs from a different directory, it's fine to import this way
# pylint: disable=W0403

from xceptions import DockerTestNAError
import bugzilla
import logging

class Trackers(object):
    """
    This class provides a simple interface to initalize and run
    all trackers at once for a subtest.
    :param subtest: The Subtest object which to set trackers for.
    """
    def __init__(self, subtest):
        bz_blockers = BugzillaBlocker(subtest)
        bz_blockers.skip_if_blockers()


class BugzillaBlocker(object):
    """
    This class connects to bugzilla and provides functionality that
    will skip a subtest if there is an open bug against it.
    :param subtest: The Subtest object this bugzilla blocker is attached to.
    """
    def __init__(self, subtest):
        self.subtest = subtest
        config = subtest.config

        def get_conf(field):
            """ Safe way to get config field """
            if field in config:
                return config[field]
            else:
                return None

        #the bugzilla module is very noisy
        log = logging.getLogger("bugzilla")
        log.setLevel(logging.WARNING)
        log = logging.getLogger("urllib3")
        log.setLevel(logging.WARNING)

        url = config['bugzilla_url']
        username = get_conf('bugzilla_username')
        password = get_conf('bugzilla_password')
        self.rhbz = bugzilla.Bugzilla(url=url)
        if username and password:
            self.rhbz.login(user=username, password=password)

        self.fixed_states = config['bugzilla_fixed_states'].split(',')

        blockers = get_conf('bugzilla_blockers')
        if blockers:
            if isinstance(blockers, (str, unicode)):
                self.blockers = [int(x) for x in blockers.split(',')]
            else:
                self.blockers = [blockers]
        else:
            self.blockers = []

        self.enabled = config['bugzilla_enable']

    def get_open_bzs(self):
        """
        This method returns a list of bugs that are not in a closed state
        :return: List of open bugs
        """
        bugs = self.rhbz.getbugs(self.blockers)
        bzs = [x.id for x in bugs if x.status not in self.fixed_states]
        return bzs

    def skip_if_blockers(self):
        """
        This method will throw a skip exception if there are blocking bugzilla
        bugs.
        :raise DockerTestNAError: If there are blocking bugs.
        """
        bugs = self.get_open_bzs()
        if self.enabled and bugs:
            raise DockerTestNAError("Skpping test due to open "
                                    "bugzilla bug(s): %s" % (bugs))
        elif self.enabled and self.blockers:
            self.subtest.loginfo("Previously blocked by bugzilla "
                                 "bug(s): %s" % (self.blockers))
