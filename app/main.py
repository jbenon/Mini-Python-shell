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


# Set up readline library
def autocompleter(text: str, state: int) -> list[str]:
    """Compares the text string with builtin command names and autocompletes them."""
    lenText = len(text)
    listMatchCommandNames = []
    # Match with builtin commands
    builtinCommands = Command.getBuiltinCommandNames()
    for commandName in builtinCommands:
        if commandName[:lenText] == text:
            listMatchCommandNames.append(commandName + " ")
    # Match with custom commands
    customCommands = []
    for directoryPath in os.environ.get("PATH", "").split(os.pathsep):
        customCommands.extend(
            [
                os.path.splitext(file)[0]
                for file in os.listdir(directoryPath)
                if (
                    os.access(os.path.join(directoryPath, file), os.X_OK)
                    and os.path.isfile(os.path.join(directoryPath, file))
                )
            ]
        )
    for commandName in customCommands:
        if commandName[:lenText] == text:
            listMatchCommandNames.append(commandName + " ")
    # Output desired state and handle missing completion
    if len(listMatchCommandNames) > 0:
        return listMatchCommandNames[state]
    else:
        sys.stdout.write("\a")  # bell command
        sys.stdout.flush()
        return None


readline.set_completer(autocompleter)
readline.parse_and_bind("tab: complete")


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
