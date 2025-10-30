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
    builtinCommands = ["exit", "echo", "type", "pwd", "cd", "cat"]
    getCommandInput = True

    def __init__(self, inputList: list[str]):
        self.command = inputList[0]
        if len(inputList) > 1:
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
                subprocess.run([self.command] + self.params)
            except Exception as e:
                sys.stdout.write(f"{e}\n")
        else:
            sys.stdout.write(f"{self.command}: command not found\n")

    def exit(self):
        """Exits the terminal."""
        if len(self.params) > 1 or self.params[0] not in ["0", "1"]:
            sys.stdout.write("exit: expects only 0 or 1\n")
            return
        if self.params[0] == "0":
            Command.getCommandInput = False

    def echo(self):
        """Displays the parameters in the shell."""
        inputString = " ".join(self.params)
        # Builds the string to actually display
        displayString = ""
        displayLiteral = False
        for iChar, char in enumerate(inputString):
            if char == "'":
                # Change display mode
                displayLiteral = not displayLiteral
                # Display if this is not a pair of single quotes
                if displayLiteral:
                    if iChar == len(inputString) - 1:
                        displayString = displayString + char
                    elif "'" not in inputString[iChar + 1 :]:
                        displayString = displayString + char
            elif char == " ":
                if displayLiteral:
                    displayString = displayString + char
                else:
                    if len(displayString) == 0 or displayString[-1] != " ":
                        displayString = displayString + char
            else:
                displayString = displayString + char
        # Actually displays
        sys.stdout.write(f"{displayString}\n")

    def type(self):
        """Displays the type of the parameter command."""
        if len(self.params) > 1:
            sys.stdout.write("type: expects only one parameter\n")
            return
        if self.isValidBuiltin(self.params[0]):
            sys.stdout.write(f"{self.params[0]} is a shell builtin\n")
        else:
            # Search for command in PATH
            executablePath = shutil.which(self.params[0], mode=os.X_OK)
            if executablePath:
                sys.stdout.write(f"{self.params[0]} is {executablePath}\n")
            else:
                sys.stdout.write(f"{self.params[0]}: not found\n")

    def pwd(self):
        """Displays the current working directory."""
        if self.params is not None:
            sys.stdout.write("pwd: expects no parameter\n")
            return
        sys.stdout.write(f"{os.getcwd()}\n")

    def cd(self):
        """Changes working directory to a target path (absolute, relative, or HOME)."""
        if len(self.params) > 1:
            sys.stdout.write("cd: expects only one parameter\n")
            return
        if self.params[0] == "~":
            os.chdir(os.environ["HOME"])
        elif os.path.isdir(self.params[0]):
            os.chdir(self.params[0])
        else:
            sys.stdout.write(f"cd: {self.params[0]}: No such file or directory\n")

    def cat(self):
        """Displays the content of the file given in parameter."""
        # Clean the list of parameters to extract paths enclosed by single quotes
        inputPaths = " ".join(self.params)
        inputPaths = inputPaths.split("'")
        cleanPaths = []
        for path in inputPaths:
            if len(path) == 0 or path == len(path) * path[0]:
                pass
            else:
                cleanPaths.append(path)
        # Display file content
        for iPath, path in enumerate(cleanPaths):
            try:
                with open(path, "r") as file:
                    sys.stdout.write(file.read())
                # Print separation or line break
                if iPath == len(cleanPaths) - 1:
                    sys.stdout.write("\n")
                else:
                    sys.stdout.write(" ")
            except Exception as e:
                sys.stdout.write(f"{e}\n")


if __name__ == "__main__":
    main()
