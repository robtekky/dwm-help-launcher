import pytest

from wm_help_launcher import __version__
from wm_help_launcher.bin import wm_helper


@pytest.fixture(name="config_file")
def fixture_config_file(tmp_path):
    _dir = tmp_path / "git" / "dwm"
    _dir.mkdir(parents=True)
    yield _dir / "config.h"


def test_version():
    assert isinstance(__version__, str)


def test_get_keybindings_dict__ok(config_file):
    config_file.write_text("""/*d* A+S F1 This is the first keybinding */\n
    /*d* C+A k This is the second keybinding */\n
    /*d* A+C g This is the third keybinding */\n
    /*d* 0 XF86XK_AudioMute This is the fourth keybinding */""")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))
        kb_dict = wm_helper.get_keybindings_dict()

    assert kb_dict == {
        ('AS', 'F1'): 'This is the first keybinding',
        ('AC', 'k'): 'This is the second keybinding',
        ('AC', 'g'): 'This is the third keybinding',
        ('0', 'XF86XK_AudioMute'): 'This is the fourth keybinding',
    }


@pytest.mark.parametrize(
    "modifiers",
    ["D", "0+1", "C+0"]
)
def test_get_keybindings_dict__invalid_modifier(config_file, modifiers):
    config_file.write_text(f"/*d* {modifiers} F1 This is the a keybinding */")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))

        with pytest.raises(SystemExit) as exit_mock:
            _ = wm_helper.get_keybindings_dict()

    assert exit_mock.type == SystemExit
    assert exit_mock.value.code.startswith("Found the following line containing invalid modifier/s:")


def test_get_keybindings_dict__duplicate_modifiers(config_file):
    config_file.write_text("/*d* M+S+C+M XF86XK_AudioMute This is the a keybinding */")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))

        with pytest.raises(SystemExit) as exit_mock:
            _ = wm_helper.get_keybindings_dict()

    assert exit_mock.type == SystemExit
    assert exit_mock.value.code.startswith("Found the following line with duplicate modifiers included:")


@pytest.mark.parametrize(
    "modifiers",
    ["C+A", "A+C"]
)
def test_get_keybindings_dict__reserved_keybinding(config_file, modifiers):
    config_file.write_text(f"/*d* {modifiers} F5 This is the a keybinding */")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))

        with pytest.raises(SystemExit) as exit_mock:
            _ = wm_helper.get_keybindings_dict()

    assert exit_mock.type == SystemExit
    assert exit_mock.value.code.startswith("Found the following line using a reserved keybinding:")


def test_get_keybindings_dict__duplicate_keybinding(config_file):
    config_file.write_text("""/*d* A+S F1 This is the first keybinding */\n
    /*d* C+A k This is the second keybinding */\n
    /*d* A+C g This is the third keybinding */\n
    /*d* A+S F1 This is the fourth keybinding */""")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))

        with pytest.raises(SystemExit) as exit_mock:
            _ = wm_helper.get_keybindings_dict()

    assert exit_mock.type == SystemExit
    assert exit_mock.value.code.startswith("Found the following line with a duplicate keybinding:")


@pytest.mark.parametrize(
    "modifiers, expected_translation",
    [("CA", "Control+Alt"),
     ("MS", "Super+Shift")]
)
def test_translate_modifiers__regular_modifiers(modifiers, expected_translation):
    key = "U"
    translation = wm_helper.translate_modifiers(key, modifiers)

    assert translation == f"{key}+{expected_translation}"


def test_translate_modifiers__0_modifier():
    key = "U"
    translation = wm_helper.translate_modifiers(key, "0")

    assert translation == key


def test_main__validation_mode(config_file, capsys):
    config_file.write_text("""/*d* 0 XF86XK_AudioMute This is the first keybinding */\n
    /*d* C+A k This is the second keybinding */\n
    /*d* A+C g This is the third keybinding */\n
    /*d* A+S F1 This is the fourth keybinding */""")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))
        wm_helper.main("validation")

    out, _ = capsys.readouterr()

    assert out == "✅ Validation of 4 keybindings in config.h succeeded!!!\n"


def test_main__key_mode(config_file, capsys):
    config_file.write_text("""/*d* A+S F1 This is the first keybinding */\n
    /*d* C+A k This is the second keybinding */\n
    /*d* 0 XF86XK_Calculator This is the third keybinding */\n
    /*d* A+C g This is the fourth keybinding */""")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("HOME", str(config_file.parent.parent.parent))
        wm_helper.main("key")

    out, _ = capsys.readouterr()

    assert out == (
        "F1+Alt+Shift This is the first keybinding\n"
        "k+Alt+Control This is the second keybinding\n"
        "g+Alt+Control This is the fourth keybinding\n"
        )
