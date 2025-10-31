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

        # Execute
        if command.isValid():
            commandOutput = command.execute()
            # Display or write
            if commandOutput is not None:
                if command.fileOutput == "":
                    sys.stdout.write(commandOutput)
                else:
                    with open(command.fileOutput, "w") as file:
                        file.write(commandOutput)


if __name__ == "__main__":
    main()
