import sys
import os

try:
    # When run as a package
    from .commands import Command
    from . import commands
    from . import autocompletion
except ImportError:
    # When run locally as a script
    from commands import Command
    import commands
    import autocompletion


def main():
    builtinCommands = Command.getBuiltinCommandNames()
    command = Command()

    # Configure autocompletion
    autocompletion.setupCompletion()

    # Read history file
    try:  # Load envirponment history file
        histFilePath = os.environ["HISTFILE"]
        historyCommand = commands.HistoryCommand(f"history -r {histFilePath}")
        historyCommand.execute()
    except Exception:
        try:  # Load local history file
            histFilePath = os.path.join(os.getcwd(), "app", "history.txt")
            historyCommand = commands.HistoryCommand(f'history -r "{histFilePath}"')
            historyCommand.execute()
        except Exception:
            pass

    while command.parseNextCommand:
        # Get user input
        commandInput = input("$ ")

        # Parse command and determine its type
        commandVanilla = Command(commandInput)
        if commandVanilla.command in builtinCommands:
            commandType = getattr(commands, commandVanilla.command.capitalize() + "Command")
        else:
            commandType = commands.CustomCommand
        command = commandType()
        command.__dict__.update(commandVanilla.__dict__)

        # Update command history
        command.updateHistory()

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
