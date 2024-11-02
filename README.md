[![testsuite](https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon/actions/workflows/pythonapp.yml/badge.svg)](https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon/actions/workflows/pythonapp.yml)
[![codecov.io](https://codecov.io/github/castixgithub/i3-workspace-names-daemon/coverage.svg?branch=master)](https://codecov.io/github/castixgithub/i3-workspace-names-daemon?branch=master)
[![Build Deb Pack](https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon/actions/workflows/debpack.yml/badge.svg)](https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon/actions/workflows/debpack.yml)

# i3-workspace-names-daemon

This script dynamically updates [i3wm](https://i3wm.org/) workspace names based on the names of the windows therein.

It also allows users to define an icon to show for a named window from the [Font Awesome](https://origin.fontawesome.com/icons?d=gallery) icon list or other system wide icon fonts.

### tl;dr
update i3-bar workspace names to look something like this

<img src="https://raw.githubusercontent.com/cboddy/_vim_gifs/master/i3-bar-with-icons.png"></img>

> [!NOTE]
> This is a fork, the original is [here](https://github.com/cboddy/i3-workspace-names-daemon)

### install

#### Archlinux

<strike>There is this [AUR package](https://aur.archlinux.org/packages/i3-workspace-names-daemon-git)</strike> (it was deleted due to it being marked as duplicate of cboddy's original)

PKGBUILD is [here](https://github.com/i3-workspace-names-daemon/AUR)

#### Gentoo
[ebuild repository](https://github.com/i3-workspace-names-daemon/gentoo) available

```bash
eselect repository add i3-workspace-names-daemon git https://github.com/i3-workspace-names-daemon/gentoo
emerge --sync i3-workspace-names-daemon
echo "x11-misc/i3-workspace-names-daemon **" >/etc/portage/package.accept_keywords/i3-workspace-names-daemon
echo "dev-python/i3ipc **" >/etc/portage/package.accept_keywords/i3ipc
emerge --ask x11-misc/i3-workspace-names-daemon
```

#### Debian & others

You can download the latest Debian package (`.deb`) file and its MD5 checksum from
the [Releases](https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon/releases) section.

1. **Download the Package and Checksum**  
   Go to the [Releases page](https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon/releases) and
   download both:
    - The `.deb` file for the package
    - The corresponding `.md5` checksum file


2. **Verify the Download (optional but recommended)**  
   To verify the integrity of the downloaded `.deb` file, compare its MD5 checksum with the provided checksum:
    ```bash
    md5sum -c i3-workspace-names-daemon_0.15.2_amd64.deb.md5
    ```
   If the checksum matches, you’ll see an `OK` message, confirming the file is intact.


3. **Install the Package**  
    Once verified, you can install the package using `apt-get`:
    ```bash
   sudo apt-get install ./i3-workspace-names-daemon_0.15.2_amd64.deb
    ```

#### pip

The pypi package is still pointing to a legacy (with less features but working) version.

Until Chris comes back, install manually

#### manual installation

1. install git, python, fontawesome, python-i3ipc

2. clone this repository
```bash
git clone https://github.com/i3-workspace-names-daemon/i3-workspace-names-daemon
cd i3-workspace-names-daemon
```

3. install with pip
```bash
pip install --user -e .
```

4. to update simply `git pull`

##### font 

You can use all icon fonts available on your system thanks to pango. [More here](#more-icons-with-pango).


You can install the [Font Awesome](https://origin.fontawesome.com/icons?d=gallery) font via your favourite package manager. This is necessary if you want to show an icon instead of a window's name in the i3 status bar.  

For Debian/Ubuntu et al. 

```
sudo apt install fonts-font-awesome
```
_Note that the Debian package is usually behind the current version of Font Awesome. If you want to use a more up to date version, [download the free Package](https://fontawesome.com/download) and install manually (Tutorial for Ubuntu 22.04 [here](https://linuxconfig.org/how-to-install-fonts-on-ubuntu-22-04-jammy-jellyfish-linux))._

**NB: if the glyphs are not rendering make sure the font is installed.**


### i3 config

Add the following line to your ``~/.i3/config``.

```
exec_always --no-startup-id exec i3-workspace-names-daemon
```

### icons config
Configure what icons to show for what application-windows in the file  ``~/.i3/app-icons.json`` or ``~/.config/i3/app-icons.json`` (in JSON format). For example:

```
chris@vulcan: ~$ cat ~/.config/i3/app-icons.json
{
    "firefox": "firefox",
    "chromium-browser": "chrome",
    "chrome": "chrome",
    "google-chrome": "chrome",
    "x-terminal-emulator": "terminal",
    "thunderbird": "envelope",
    "jetbrains-idea-ce": "file-pen",
    "nautilus": "folder-open",
    "clementine": "music",
    "vlc": "play",
    "signal": "comment",
    "_no_match": "question"
}
```

NB: to validate your config file is formatted correctly run this command and check it doesn't  report an error

```
python3 -m json.tool  /path/to/your/app-icons.json
```

NB: to further validate the icon names are all existing you can try run the daemon manually

where the key is the name of the i3-window (ie. what is shown in the i3-bar when it is not configured yet) and  the value is the font-awesome icon name you want to show instead, see [picking icons](#picking-icons).

Note: the hard-coded list above is used if you don't add this icon-config file.

### matching windows

You can debug windows names with `xprop`

Windows names are detected by inspecting in the following priority
- name
- title
- instance
- class

If there is no window name available a question mark is shown instead.

Another (simpler) way for debugging window names is running this script with `-v` or `--verbose` flag, it is suggested to use a terminal emulator that supports unicode (eg. kitty or urxvt)

### unrecognised windows

If a window is not in the icon config then by default the window title will be displayed instead.

The maximum length of the displayed window title can be set with the command line argument `--max_title_length` or `-l`.

To show a specific icon in place of unrecognised windows, specify an icon for window `_no_match` in the icon config.
If you want to show only that icon (hiding the name) then use the `--no-match-not-show-name` or `-n` option.

To hide all unknown applications, use the `--ignore-unknown` or `-i` option.

### windows delimiter

The window delimiter can be specified with `-d` or `--delimiter` parameter by default it is `|`.

### picking icons 

The easiest way to pick an icon is to search for one in the [gallery](https://origin.fontawesome.com/icons?d=gallery). **NB: the "pro" icons are not available in the debian package.**

### more icons with pango

As the i3bar supports [pango markup](https://developer.gnome.org/pygtk/stable/pango-markup-language.html), you can use almost all (icon-)fonts available on your system.
Custom text can be used instead of icons too.
All icon definitions starting with the `<` character will be interpreted as pango markup.

To check which fonts are available for use in pango, run the command
```
pango-list
```

To *test* if you properly installed all required fonts and the markup is valid, you can use the following command,
assuming you installed the [file-icons](https://github.com/file-icons/icons/blob/master/charmap.md) or [all-the-icons](https://github.com/domtronn/all-the-icons.el/blob/master/data/data-fileicons.el) fonts (links are to the current page with codes that you need to put in the markup, not the homepage of the fonts):
```bash
echo -e '<span font_desc="file-icons">\ue926</span>' | pango-view --markup /dev/stdin
```

It should render the markup correctly. If not, you need to check your font installation.

#### example: firefox & emacs

<img src="https://user-images.githubusercontent.com/1242917/80286549-5b66dc80-872c-11ea-8d3a-db1488ff299c.png"></img>

The following example displays an emacs icon for all instances of emacs and the text "FF" in red for every firefox instance.

```json
{
    "firefox": "<span foreground=\"red\">FF</span>",
    "emacs": "<span font_desc=\"file-icons\">\ue926</span>"
}
```

### dynamic icon titles with `transform_title`

Some applications display the title of the current project in the window title to differentiate between multiple instances.
This information can be displayed in the i3bar by using the `transform_title` directive.

Instead of a single string for the icon definition, use a json object as the property. 
For the title transformation the property `transform_title` is required.

#### `on`

The window identifier to be used, the same as in [matching windows](#matching-windows) paragraph, defaults to `window_title` that should be good for most of the use cases

#### `from`

The `from` property defines a regex which must match the title of the window.
If the window title is not matched, no output will be shown.
To match any window title, use `.*` as the value.
Use capturing groups (`()`) to capture strings, which you can use in the transformation (as `\1`, `\2`, `\3`, …).
Remember to escape backslashes with another backslash.

#### `to`

The string that will be displayed.
You can use strings that were matched by capturing groups in the `from` regex.

#### `compress`

Enables shortening the resulting displayed strings in a more recognizable name.
The name is split into groups of alphanumeric strings, which are all cut to a length of 3 and joined together using the adjacent separator in the original string.
This is applied after `from` -> `to` regex modification is done.
Example: `i3-workspace_names+daemon` → `i3-wor_nam+dae`

#### example: emacs project title

<img src="https://user-images.githubusercontent.com/1242917/80287066-91f22680-872f-11ea-93ec-ddaab989cfab.png"></img>

Emacs displays the current project in brackets (`[<project name>]: <file name>`).
The project name can be matched by the capturing group in this regex: `".*\\[(.+?)\\].*"`.
Only the project name is shown as a result of the `to` property.

```json
"emacs": {
  "transform_title": {
    "from": ".*\\[(.+?)\\].*",
    "to": "\\1",
    "compress": true
  },
  "icon": "<span font_desc=\"file-icons\">\ue926</span>"
}
```

### Static/Fixed Workspace Name

When you insert a workspace number instead of an application name,
you can then set the icon and name

example
```json
"1": {
    "icon": "file-pen",
    "title": "editor",
},
"2": "firefox",
```
