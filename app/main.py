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
    builtinCommands = ["exit", "echo", "type", "pwd", "cd"]
    getCommandInput = True

    def __init__(self, inputList: list[str]):
        # Clean all parameters to account for single and double quotes
        self.params = None
        inputParamsString = " ".join(inputList)
        self.params = []
        isBetweenSingleQuotes = False
        isBetweenDoubleQuotes = False
        escapeNextChar = False
        escapeNextCharDoubleQuote = False
        currentParam = ""
        for iChar, char in enumerate(inputParamsString):
            if escapeNextChar:
                currentParam = currentParam + char
                escapeNextChar = False
            elif escapeNextCharDoubleQuote:
                if char in ['"', "\\", "$", "`"]:
                    currentParam = currentParam + char
                else:
                    currentParam = currentParam + "\\" + char
                escapeNextCharDoubleQuote = False
            else:
                match char:
                    case "\\":
                        if isBetweenSingleQuotes:
                            currentParam = currentParam + char
                        else:
                            if isBetweenDoubleQuotes:
                                escapeNextCharDoubleQuote = True
                            else:
                                escapeNextChar = True
                    case "'":
                        currentParam, isBetweenSingleQuotes = self.updateParamQuote(
                            char,
                            isBetweenSingleQuotes,
                            isBetweenDoubleQuotes,
                            currentParam,
                            iChar,
                            inputParamsString,
                        )
                    case '"':
                        currentParam, isBetweenDoubleQuotes = self.updateParamQuote(
                            char,
                            isBetweenDoubleQuotes,
                            isBetweenSingleQuotes,
                            currentParam,
                            iChar,
                            inputParamsString,
                        )
                    case " ":
                        if isBetweenSingleQuotes or isBetweenDoubleQuotes:
                            currentParam = currentParam + char
                        else:
                            # Start new block delimited by a space
                            if len(currentParam) > 0:
                                self.params.append(currentParam)
                                currentParam = ""
                    case _:
                        currentParam = currentParam + char
        if len(currentParam) > 0:
            self.params.append(currentParam)
        # Separate the command and arguments
        if len(self.params) > 0:
            self.command = self.params[0]
        if len(self.params) > 1:
            self.params = self.params[1:]
        else:
            self.params = None

    def updateParamQuote(
        self,
        quoteType: str,
        isBetweenTargetQuoteType: bool,
        isBetweenOtherQuoteType: bool,
        currentParam: str,
        iChar: int,
        inputParamsString: str,
    ) -> tuple[str, bool]:
        """Util function called when a quote character is encountered when cleaning parameters during initialisation."""
        # Treats the quote as any other character if we're already in a quote block
        if isBetweenOtherQuoteType:
            currentParam = currentParam + quoteType
        else:
            ignoreQuote = False
            # Ignore if this is a pair of empty quotes
            if iChar < (len(inputParamsString) - 1) and inputParamsString[iChar + 1] == quoteType:
                ignoreQuote = True
            elif iChar > 0 and inputParamsString[iChar - 1] == quoteType:
                ignoreQuote = True
            # Change character storage settings
            else:
                isBetweenTargetQuoteType = not isBetweenTargetQuoteType
            # Store quote literally if this is not a pair of quotes
            if isBetweenTargetQuoteType and (
                iChar == len(inputParamsString) - 1 or quoteType not in inputParamsString[iChar + 1 :]
            ):
                isBetweenTargetQuoteType = False
                currentParam = currentParam + quoteType
            # Start a block between quotes
            if isBetweenTargetQuoteType and len(currentParam) > 0 and not ignoreQuote:
                self.params.append(currentParam)
                currentParam = ""
        return currentParam, isBetweenTargetQuoteType

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
        sys.stdout.write(f"{' '.join(self.params)}\n")

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


if __name__ == "__main__":
    main()
