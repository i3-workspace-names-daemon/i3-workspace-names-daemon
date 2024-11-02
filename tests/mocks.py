class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class MockLeaf:
    def __init__(self, name, title=None, instance=None, wc=None, ai=None):
        self.name = name
        if title is not None:
            self.window_title = title
        else:
            self.window_title = name
        if instance is not None:
            self.window_instance = instance
        else:
            self.window_instance = name
        if wc is not None:
            self.window_class = wc
        else:
            self.window_class = name
        if ai is not None:
            self.app_id = ai
        else:
            self.app_id = name


class MockWorkspace:
    def __init__(self, num, *leaves):
        self.num = num
        self.leaves_ = leaves
        self.visible = True
        self.focused = True
        self.name = ""

    def leaves(self):
        return self.leaves_


class MockTree:
    def __init__(self, mi3):
        self.mi3 = mi3

    def workspaces(self):
        return self.mi3.workspaces


class MockI3:
    def __init__(self, *workspaces):
        self.workspaces = workspaces

    def get_tree(self):
        return MockTree(self)

    def get_workspaces(self):
        return self.workspaces

    def command(self, cmd):
        self.cmd = cmd

    def on(self, _case, rename):
        self.rename = rename

    def main(self):
        self.rename(self, None)
