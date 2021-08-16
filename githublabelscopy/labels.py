from getpass import getpass

import yaml
from github import Github


class Labels(object):
    def __init__(self, token=None, login=None, base_url=None):
        self.src_labels = dict()
        self.dst_labels = dict()
        self._identify(token, login, base_url)
        self._dumpMode = False
        self._labels = dict()

    def _identify(self, token=None, login=None, base_url=None):
        if token:
            if base_url:
                self.github = Github(token, base_url=base_url)
            else:
                self.github = Github(token)
        elif login:
            if base_url:
                self.github = Github(login, getpass(), base_url=base_url)
            else:
                self.github = Github(login, getpass())
        else:
            if base_url:
                self.github = Github(base_url=base_url)
            else:
                self.github = Github()

    def setSrcRepo(self, repository):
        self.src_repo = self.github.get_repo(repository)
        src_original_labels = self.src_repo.get_labels()
        self.src_labels = {label.name: label.color
                           for label in src_original_labels}

    def setDstRepo(self, repository):
        self.dst_repo = self.github.get_repo(repository)
        self.dst_original_labels = self.dst_repo.get_labels()
        self.dst_labels = {label.name: label.color
                           for label in self.dst_original_labels}

    def load(self, filename):
        with open(filename, 'r') as fh:
            self.src_labels = yaml.load(fh.read())

    def activateDumpMode(self):
        self._dumpMode = True

    def dump(self):
        return yaml.dump(self._labels)

    def listLabels(self):
        return self.src_labels

    def getMissing(self):
        "Get missing labels from source repository into destination."
        return {name: color for name, color in self.src_labels.items()
                if name not in self.dst_labels.keys()}

    def getWrong(self):
        "Get labels with wrong color in destination repository from source."
        return {name: color for name, color in self.src_labels.items()
                if name in self.dst_labels.keys() and
                color != self.dst_labels[name]}

    def getBad(self):
        "Get labels from destination repository not in source."
        return {name: color for name, color in self.dst_labels.items()
                if name not in self.src_labels.keys()}

    def createMissing(self):
        "Create all missing labels from source repository in destination."
        missings = self.getMissing()
        self._labels.update(missings)
        if not self._dumpMode:
            for name, color in missings.items():
                print("Creating {}".format(name))
                self.dst_repo.create_label(name, color)

    def updateWrong(self):
        wrongs = self.getWrong()
        self._labels.update(wrongs)
        if not self._dumpMode:
            for name, color in wrongs.items():
                print("Updating {}".format(name))
                working_label = next((x for x in self.dst_original_labels
                                     if x.name == name), None)
                working_label.edit(name, color)

    def deleteBad(self):
        bads = self.getBad()
        self._labels.update(bads)
        if not self._dumpMode:
            for name, _ in bads.items():
                print("Deleting {}".format(name))
                working_label = next((x for x in self.dst_original_labels
                                     if x.name == name), None)
                working_label.delete()

    def fullCopy(self):
        self.createMissing()
        self.updateWrong()
        self.deleteBad()
