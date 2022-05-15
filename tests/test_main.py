from i3_workspace_names_daemon import main
from mocks import AttrDict, MockLeaf, MockWorkspace, MockTree, MockI3
from pytest import raises
import i3ipc


def test_main(monkeypatch):
    monkeypatch.setattr(i3ipc, 'Connection', lambda: MockI3(
        MockWorkspace(1, MockLeaf("firefox")),
        MockWorkspace(2, MockLeaf("chromium-browser")),
    ))
    main(['-c', 'tests/test-config.json'])


def test_verbose_startup(monkeypatch, capsys):
    monkeypatch.setattr(i3ipc, 'Connection', lambda: MockI3(
        MockWorkspace(1, MockLeaf("firefox")),
        MockWorkspace(2, MockLeaf("chromium-browser")),
    ))
    main(['-v', '-c', 'tests/test-config.json'])
    cap = capsys.readouterr()
    assert '-> name: firefox' in cap.out
    assert 'rename workspace "" to "1: "' in cap.out


def test_config(monkeypatch):
    monkeypatch.setattr(i3ipc, 'Connection', lambda: MockI3(
        MockWorkspace(1, MockLeaf("firefox")),
        MockWorkspace(2, MockLeaf("chromium-browser")),
    ))
    with raises(SystemExit) as ex:
        main(['-c', 'asd'])
    assert "Specified app-icon config path 'asd' does not exist" in str(ex)
