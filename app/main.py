import sys

try:
    # When run as a package
    from .commands import Command
    from . import commands
except ImportError:
    # When run locally as a script
    from commands import Command
    import commands


def main():
    builtinCommands = Command.getBuiltinCommandNames()
    command = Command()

    while command.parseNextCommand:
        # Print a prompt
        sys.stdout.write("$ ")

        # Parse command and determine its type
        commandInput = input()
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
            if resultCommand is tuple:
                outputCommand, errorCommand = resultCommand
            else:
                outputCommand = resultCommand
            if outputCommand is not None:
                if command.fileOutput == "":
                    sys.stdout.write(outputCommand)
                else:
                    with open(command.fileOutput, "w") as file:
                        file.write(outputCommand)
            if errorCommand is not None:
                if command.fileError == "":
                    sys.stdout.write(errorCommand)
                else:
                    with open(command.fileError, "w") as file:
                        file.write(errorCommand)


if __name__ == "__main__":
    main()
