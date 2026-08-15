"""
commands
========

This package holds the implementation of every individual Linksaver
command (add, view, list, ...), grouped by topic:

    prompts.py       - tiny input() wrapper shared by every command
    init_cmd.py       - `init`               create a new project config
    links_cmd.py       - `add`, `add2`, `add3`, `list`, `open`
    export_cmd.py       - `view`, `viewx`      render the config to Markdown/TXT
    imports_cmd.py      - `addpkg`, `addcargo`  import licenses from lockfiles
    submodules_cmd.py    - `addsubmodule`, `clonesubm`
    gitrepo_cmd.py       - interactive-menu wrapper for `gitrepo pack`/`restore`
                        (the real CLI entry point is handled directly in
                        cli.py via ../gitreposaver.py, since it needs its
                        own argparse flags like --encrypt/--base64)
    ui.py             - banner/help text, interactive menu, `s` status command

cli.py (one level up) only ties these together - it does not contain any
command logic itself.
"""
