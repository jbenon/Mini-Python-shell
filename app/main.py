import sys
import os
import shutil
import subprocess


def main():
    while Command.getCommandInput:
        # Print a prompt
        sys.stdout.write("$ ")

        # Parse command
        commandInput = input()
        command = Command(commandInput.split(" "))

        # Execute
        command.execute()


class Command:
    builtinCommands = ["exit", "echo", "type", "pwd"]
    getCommandInput = True

    def __init__(self, inputList: list[str]):
        self.command = inputList[0]
        if len(inputList) == 2:
            self.params = inputList[1]
        elif len(inputList) > 2:
            self.params = inputList[1:]
        else:
            self.params = None

    def isValidBuiltin(self, target: str = "") -> bool:
        """Checks whether a command is builtin."""
        if target != "":
            return target in Command.builtinCommands
        else:
            return self.command in Command.builtinCommands

    def isValidExecutable(self, target: str = "") -> bool:
        """Checks whether a command exists and is executable."""
        if target != "":
            return shutil.which(target, mode=os.X_OK)
        else:
            return shutil.which(self.command, mode=os.X_OK)

    def execute(self):
        """Calls the method to execute a builtin command, or executes the custom command, or displays error."""
        if self.isValidBuiltin():
            stringMethod = "self." + self.command + "()"
            exec(stringMethod)
        elif self.isValidExecutable():
            try:
                subprocess.run(self.command + self.params)
            except Exception as e:
                sys.stdout.write(f"{e}\n")
        else:
            sys.stdout.write(f"{self.command}: command not found\n")

    def exit(self):
        """Exits the terminal."""
        if type(self.params) is list or self.params not in ["0", "1"]:
            sys.stdout.write("The expected parameter is '0' or '1'.\n")
            return
        if self.params == "0":
            Command.getCommandInput = False

    def echo(self):
        """Displays the parameters in the shell."""
        if type(self.params) is list:
            sys.stdout.write(f"{' '.join(self.params)}\n")
        else:
            sys.stdout.write(f"{self.params}\n")

    def type(self):
        """Displays the type of the parameter command."""
        if type(self.params) is list:
            sys.stdout.write("There should be only one parameter.\n")
            return
        if self.isValidBuiltin(self.params):
            sys.stdout.write(f"{self.params} is a shell builtin\n")
        else:
            # Search for command in PATH
            executablePath = shutil.which(self.params, mode=os.X_OK)
            if executablePath:
                sys.stdout.write(f"{self.params} is {executablePath}\n")
            else:
                sys.stdout.write(f"{self.params}: not found\n")


if __name__ == "__main__":
    main()
