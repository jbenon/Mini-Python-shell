import sys
import os

import readline
import shutil

try:
    # When run as a package
    from .commands import Command
    from . import commands
except ImportError:
    # When run locally as a script
    from commands import Command
    import commands

# Cache for readline autocompleter
_ALL_COMMANDS_CACHE: list[str] | None = None


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

    # Build the list of builtin and custom commands
    if _ALL_COMMANDS_CACHE is None:
        _ALL_COMMANDS_CACHE = _getAllCommandNames()

    # Match with commands
    listMatchCommandNames = [command + " " for command in _ALL_COMMANDS_CACHE if command.startswith(text)]

    # Output desired state and handle missing completion
    if len(listMatchCommandNames) > state:
        return listMatchCommandNames[state]
    else:
        sys.stdout.write("\a")  # bell command
        sys.stdout.flush()
        return None


# Set up readline library
readline.set_completer(autocompleter)
readline.parse_and_bind("tab: complete")
readline.parse_and_bind("set show-all-if-ambiguous off")


def main():
    builtinCommands = Command.getBuiltinCommandNames()
    command = Command()

    while command.parseNextCommand:
        # Print a prompt
        sys.stdout.write("$ ")

        # Get user input
        commandInput = input()

        # Parse command and determine its type
        commandVanilla = Command(commandInput)
        if commandVanilla.command in builtinCommands:
            commandType = getattr(commands, commandVanilla.command.capitalize() + "Command")
        else:
            commandType = commands.CustomCommand
        command = commandType()
        command.__dict__.update(commandVanilla.__dict__)

        # Check validity then display the eventual error message
        errorMessage = command.isValid()
        if errorMessage is not None:
            if command.fileError == "":
                sys.stdout.write(errorMessage)
            else:
                with open(command.fileError, "w") as file:
                    file.write(errorMessage)
        # Execute then display the output and eventual error
        else:
            resultCommand = command.execute()
            if isinstance(resultCommand, tuple):
                outputCommand, errorCommand = resultCommand
            else:
                outputCommand = resultCommand
                errorCommand = None
            writeCommandResult(outputCommand, command.fileOutput, command.appendOutput)
            writeCommandResult(errorCommand, command.fileError, command.appendError)


def writeCommandResult(result: str, file: str, append: bool = False) -> None:
    """Writes the result (either output or error) of a command to a target file, or to the shell."""
    if file == "" and result is not None:
        sys.stdout.write(result)
    elif file != "":
        directory = os.path.dirname(file)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)  # creates the directory
        if append:
            openOption = "a"
        else:
            openOption = "w"
        with open(file, openOption) as file:
            if result is not None:
                file.write(result)


if __name__ == "__main__":
    main()
