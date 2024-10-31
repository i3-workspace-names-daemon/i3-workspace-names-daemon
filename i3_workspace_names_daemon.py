#!/usr/bin/env python3
"""Dynamically update i3wm workspace names based on running applications in each and optionally define an icon to show instead."""

import json
import os.path
import argparse
import re
import i3ipc
from sys import stderr, argv
from fa_icons import icons as fa_icons


I3_CONFIG_PATHS = tuple(
    os.path.expanduser(path)
    for path in (
        "~/.i3",
        "~/.config/i3",
        "~/.config/i3-regolith",
        "~/.config/regolith2/i3",
        "~/.config/regolith3/i3",
        "~/.config/regolith3/sway",
    )
)

DEFAULT_APP_ICON_CONFIG = {
    "chromium-browser": "chrome",
    "firefox": "firefox",
    "x-terminal-emulator": "terminal",
    "thunderbird": "envelope",
    "jetbrains-idea-ce": "file-pen",
    "nautilus": "folder-open",
    "clementine": "music",
    "vlc": "play",
    "signal": "comment",
}


def truncate(text, length, ellipsis="…"):
    if len(text) <= length:
        return text
    return text[:length] + ellipsis


def compress(text, length=3):
    ret = ""
    matches = re.finditer(r"[a-zA-Z0-9]+", text)
    for match in matches:
        ret += match[0][:length]
        if match.end() < (len(text) - 1):
            ret += text[match.end()]

    return ret


def build_rename(i3, mappings, fixed_ws, args):
    """Build rename callback function to pass to i3ipc.

    Parameters
    ----------
    i3: `i3ipc.i3ipc.Connection`
    mappings: `dict[str, Union[dict, str]]`
        Index of application-name regex (from i3) to icon-name (in font-awesome gallery).
    fixed_ws: `dict[str, Union[dict, str]]`
        Workspace mapping with fixed icon/title
    delim: `str`
        Delimiter to use when build workspace name from app names/icons.

    Returns
    -------
    func
        The rename callback.
    """
    form = args.number_separator_format
    delim = args.delimiter
    length = args.max_title_length
    uniq = args.uniq
    ignore_unknown = args.ignore_unknown
    no_unknown_name = args.no_match_not_show_name
    verbose = args.verbose

    def get_icon(icon_name):
        # is pango markup?
        if icon_name.startswith("<"):
            return icon_name
        if icon_name in fa_icons:
            return fa_icons[icon_name]
        return None

    def transform_title(target_mapping, window_title):
        tt = target_mapping["transform_title"]
        transform_from = "^" + tt["from"] + "$"
        transform_to = tt["to"]
        result, nr_subs = re.subn(transform_from, transform_to, window_title)

        # shorten name
        if tt.get("compress", False):
            result = compress(result)
        result = truncate(result, length)

        # try to get the icon, otherwise leave blank string
        icon = ""
        if target_mapping.get("icon", None):
            i = get_icon(target_mapping["icon"])
            if i:
                icon = i

        # did the title regex match?
        if nr_subs > 0:
            return "{}{}".format(icon, result)

        # fallback: title did not match, but icon defined
        if icon:
            return icon

    def resolve_icon_or_mapping(name, leaf):
        for name_re in mappings.keys():
            if re.match(name_re, name, re.IGNORECASE):
                # the key of the json configuration matches, we can
                # apply the mapping now
                target_mapping = mappings[name_re]

                if type(target_mapping) == str:
                    return get_icon(target_mapping)

                # is mapped to a title transformation?
                if type(target_mapping) == dict:
                    # it could be a dict, have the icon but not transform_title
                    if target_mapping.get("transform_title"):
                        window_title = getattr(
                            leaf,
                            target_mapping['transform_title'].get('on', "window_title"),
                            ""
                        )
                        return transform_title(target_mapping, window_title)
                    return get_icon(target_mapping.get('icon', ''))

    def get_app_label(leaf, length):
        # interate through all identifiers, stop when first match is found
        for identifier in ("name", "window_title", "window_instance", "window_class", "app_id"):
            name = getattr(leaf, identifier, None)
            if name is None:
                continue
            mapping = resolve_icon_or_mapping(name, leaf)
            if mapping:
                return mapping

        # no mapping was found
        if ignore_unknown:
            return None

        window_class = name
        no_match_fallback = "_no_match" in mappings and mappings["_no_match"] in fa_icons
        if window_class:
            # window class exists, no match was found
            if no_match_fallback:
                return fa_icons[mappings["_no_match"]] + (
                    "" if no_unknown_name else truncate(name, length)
                )
            return truncate(name, length)
        else:
            # no identifiable information about this window
            if no_match_fallback:
                return fa_icons[mappings["_no_match"]]
            return "?"

    def rename_fixed(workspace):
        newname = form.format(workspace.num,'')
        wsc = fixed_ws[workspace.num]
        if isinstance(wsc, str):
            newname += get_icon(wsc)
        else:
            if icon_name := fixed_ws[workspace.num].get('icon'):
                newname += get_icon(icon_name) + ' '
            if wsname := fixed_ws[workspace.num].get('name'):
                newname += wsname
        return newname

    def rename(i3, *_):
        workspaces = i3.get_tree().workspaces()
        commands = []
        for workspace in workspaces:
            if workspace.num in fixed_ws:
                newname = rename_fixed(workspace)
            else:
                names = [get_app_label(leaf, length) for leaf in workspace.leaves()]
                if uniq:
                    seen = set()
                    names = [x for x in names if x not in seen and not seen.add(x)]
                # filter empty names
                names = [x for x in names if x]
                names = delim.join(names)
                if int(workspace.num) >= 0:
                    if names:
                        newname = form.format(workspace.num, names)
                    else:
                        newname = str(workspace.num)
                else:
                    newname = names

            if workspace.name != newname:
                commands.append(
                    'rename workspace "{}" to "{}"'.format(
                        # escape any double quotes in old or new name.
                        workspace.name.replace('"', '\\"'),
                        newname.replace('"', '\\"'),
                    )
                )
                if verbose:
                    print(commands[-1])

        # we have to join all the activate workspaces commands into one or the order
        # might get scrambled by multiple i3-msg instances running asyncronously
        # causing the wrong workspace to be activated last, which changes the focus.
        i3.command(u";".join(commands))

    return rename


def _get_i3_dir():
    # standard i3-config directories
    for path in I3_CONFIG_PATHS:
        if os.path.isdir(path):
            return path
    raise SystemExit(
        "Could not find i3 config directory! Expected one of {} to be present".format(
            I3_CONFIG_PATHS
        )
    )


def _get_mapping(config_path=None):
    """Get app-icon mapping from config file or use defaults.

    Parameters
    ----------
    config_path: `str|None`
        Path to app-icon config file.

    Returns
    -------
    dict[str, Union[dict, str]]
        Index of application-name (from i3) to icon-name (in font-awesome gallery).

    Raises
    ------
    json.decoder.JSONDecodeError
        When app-icon config file is not in JSON format.

    SystemExit
        When `config_path is not None` and there is not a file available at tht path.
        When ~/.i3 or ~/.config/i3 is not a directory (ie. i3 is not installed).

    Notes
    -----
    If config_path is None then the locations ~/.i3/app-icons.json and ~/.config/i3/app-icons.json will also be used if available. If they are also not available then `DEFAULT_APP_ICON_CONFIG` will be used.
    """

    if config_path:
        if not os.path.isfile(config_path):
            raise SystemExit(
                "Specified app-icon config path '{}' does not exist".format(config_path)
            )
    else:
        config_path = os.path.join(_get_i3_dir(), "app-icons.json")

    if os.path.isfile(config_path):
        with open(config_path) as f:
            mappings = json.load(f)
        # normalise app-names to lower
        return {k.lower(): v for k, v in mappings.items()}
    else:
        print("Using default app-icon config {}".format(DEFAULT_APP_ICON_CONFIG))
        return dict(DEFAULT_APP_ICON_CONFIG)


def _verbose_startup(i3):
    for w in i3.get_tree().workspaces():
        print('WORKSPACE: "{}"'.format(w.name))
        for i, l in enumerate(w.leaves()):
            print(
                """===> leave: {}
-> name: {}
-> window_title: {}
-> window_instance: {}
-> window_class: {}
-> app_id: {}""".format(
                    i, l.name, l.window_title, l.window_instance, l.window_class, l.app_id
                )
            )


def _is_valid_re(regex):
    try:
        re.compile(regex)
        return True
    except:
        return False


def _validate_dict_mapping(app, mapping):
    err = False
    if type(mapping) != dict:
        print("Specified mapping for app '{}' is not a dict!".format(app))
        return False
    if mapping.get("transform_title", None):
        # a title transformation exists
        tt = mapping["transform_title"]

        if tt.get("from", None):
            if not _is_valid_re(tt["from"]):
                err = True
                print(
                    "Title transform mapping for app '{}' contains invalid regular expression in 'from' attribute!".format(
                        app
                    ),
                    file=stderr,
                )
        else:
            err = True
            print(
                "Title transform mapping for app '{}' requires a 'from' key!".format(
                    app
                ),
                file=stderr,
            )

        if not tt.get("to", None):
            err = True
            print(
                "Title transform mapping for app '{}' requires a 'to' key!".format(app),
                file=stderr,
            )

    return err


def _validate_config(config):
    # check for missing icons and wrong configurations
    err = False
    for app, value in config.items():
        icon_name = None
        if type(value) == str:
            icon_name = value
        else:
            # icon is optional when using a transform mapping
            icon_name = value.get("icon", None)
            if _validate_dict_mapping(app, value):
                err = True

        # make exceptions for custom-defined pango fonts
        if (
            icon_name is not None
            and not icon_name.startswith("<")
            and icon_name not in fa_icons
        ):
            err = True
            print(
                "Specified icon '{}' for app '{}' does not exist!".format(
                    icon_name, app
                ),
                file=stderr,
            )

    return err


def generate_icons(icons_json_path: str):  # pragma: no cover
    # icons.json is located in the metadata directory of a kit https://fontawesome.com/download
    with open(icons_json_path, "r", encoding='utf-8') as _file:
        data = json.load(_file)

    with open("fa_icons.py", "w", encoding='ascii') as _file:
        _file.write("# font-awesome icon-name to unicode mapping\n\n")
        _file.write("icons = {\n")
        for name, prop in data.items():
            if prop["free"]:
                _file.write(f'    "{name}": u"\\u{prop["unicode"].zfill(4)}",\n')
        _file.write('}\n')


def main() -> int:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "--bypass-validation",
        help="Meant for development only",
        required=False,
        action='store_true',
        default=False,
    )
    parser.add_argument(
        "-config-path",
        help=("Path to file that maps applications to icons in json format."
              " Defaults to ~/.i3/app-icons.json or ~/.config/i3/app-icons.json or"
              " hard-coded list if they are not available."),
        required=False,
    )
    parser.add_argument(
        "-s",
        "--number-separator-format",
        help=('Format of the workspace number + names/icons.'
              ' The first "{}" represents the workspace number placeholder and the second represents'
              ' the names/icons placeholder.\nEx: - "{}: {}" (Default)\n - "{} - {}"\n - "{} ( {} )"'),
        required=False,
        default="{}: {}",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        help="The delimiter used to separate multiple window names in the same workspace.",
        required=False,
        default="|",
    )
    parser.add_argument(
        "-l",
        "--max-title-length",
        help="Truncate title to specified length.",
        required=False,
        default=12,
        type=int,
    )
    parser.add_argument(
        "-u",
        "--uniq",
        help="Remove duplicate icons.",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-i",
        "--ignore-unknown",
        help="Ignore apps without a icon definitions.",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-n",
        "--no-match-not-show-name",
        help="Don't display the name of unknown apps besides the fallback icon '_no_match'.",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose startup that will help you to find the right match name for applications.",
        action="store_true",
        required=False,
        default=False,
    )
    parser.add_argument(
        "-g",
        "--generate-icons",
        help=("Instead of running the daeamon, generates fa_icon.py file. "
              "This is intented for usage with newer versions of fontawesome. "
              "For the mantainers of this program"),
        required=False,
    )
    args = parser.parse_args()

    if args.generate_icons:  # pragma: no cover
        generate_icons(args.generate_icons)
        return 0

    mappings = _get_mapping(args.config_path)

    ws = {int(wsn): wsc for wsn, wsc in mappings.items() if wsn.isdigit()}
    for wsn in ws.keys():
        del mappings[str(wsn)]

    if not args.bypass_validation and _validate_config(mappings):  # pragma: no cover
        print("Errors in configuration found!", file=stderr)
        return 0

    # build i3-connection
    i3 = i3ipc.Connection()
    if args.verbose:
        _verbose_startup(i3)

    rename = build_rename(i3, mappings, ws, args)
    for _case in [
        *[f"window::{ev}" for ev in ("move", "new", "title", "close")],
        "workspace::init",
    ]:
        i3.on(_case, rename)
    rename(i3)  # call @startup
    i3.main()
    return 0


if __name__ == "__main__":  # pragma: no cover
    main()
