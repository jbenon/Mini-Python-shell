import sys
from .commands import Command
from . import commands


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
        command.execute()


if __name__ == "__main__":
    main()
