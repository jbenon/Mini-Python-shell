import sys
import os

try:
    # When run as a package
    from .commands import Command
except ImportError:
    # When run locally as a script
    from commands import Command

import readline

# Cache for readline autocompleter
_ALL_COMMANDS_CACHE: list[str] | None = None
_LAST_BUF = None


# Utils for readline autocompleter
def _getAllCommandNames() -> list[str]:
    """Gets the names of all builtin and custom commands."""
    builtinCommands = Command.getBuiltinCommandNames()
    customCommands = []
    for directoryPath in os.environ.get("PATH", "").split(os.pathsep):
        if not directoryPath:
            continue
        try:
            files = os.listdir(directoryPath)
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            continue
        customCommands.extend(
            [
                os.path.splitext(file)[0]
                for file in files
                if (
                    os.access(os.path.join(directoryPath, file), os.X_OK)
                    and os.path.isfile(os.path.join(directoryPath, file))
                )
            ]
        )
    return builtinCommands + customCommands


# Set up readline autocompleter
def autocompleter(text: str, state: int) -> list[str]:
    """Compares the text string with builtin command names and autocompletes them."""
    global _ALL_COMMANDS_CACHE
    global _LAST_BUF

    # Build the list of builtin and custom commands
    if _ALL_COMMANDS_CACHE is None:
        _ALL_COMMANDS_CACHE = _getAllCommandNames()

    # Match with commands
    listMatchCommandNames = [command for command in _ALL_COMMANDS_CACHE if command.startswith(text)]

    # Handle ambiguous cases: display all matches on 2nd TAB only
    if state == 0:
        if len(listMatchCommandNames) == 1:  # Unambiguous match
            return listMatchCommandNames[0] + " "
        else:  # Ambiguous match
            if text != _LAST_BUF:  # 1st TAB
                _LAST_BUF = text
                sys.stdout.write("\a")
                sys.stdout.flush()
            else:  # 2nd TAB
                _LAST_BUF = text
                print()
                print("  ".join(sorted(listMatchCommandNames)))
                sys.stdout.write(f"$ {text}")
                sys.stdout.flush()

    # Return desired match
    if len(listMatchCommandNames) > state:
        return listMatchCommandNames[state] + " "
    else:
        return None


def setupCompletion() -> None:
    """Configurates the readline module with the custom completer function."""
    readline.parse_and_bind("tab: complete")
    readline.set_completer(autocompleter)


def setupHistory() -> None:
    """Configurates the readline module to have a simple interactive history of commands."""
    HISTFILE = os.path.expanduser("~/.history")
    readline.read_history_file(HISTFILE)
