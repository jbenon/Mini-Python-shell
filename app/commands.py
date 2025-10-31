import sys
import os
import shutil
import subprocess


class Command:
    def __init__(self, inputString: str = ""):
        # By default, keep looking for other commands
        self.parseNextCommand = True

        listArgs = self.parseInputIntoCommand(inputString)
        # Separate the command and arguments
        if len(listArgs) > 0:
            self.command = listArgs[0]
        else:
            self.command = None
        if len(listArgs) > 1:
            self.args = listArgs[1:]
        else:
            self.args = []

        # Redirect command outputs
        self.fileOutput = ""
        for iArg in range(len(self.args) - 1):
            if self.args[iArg] == ">" or self.args[iArg] == "1>":
                self.fileOutput = self.args[iArg + 1]
                self.args = self.args[:iArg]

    def parseInputIntoCommand(self, inputString: str = "") -> list[str]:
        """Parses the input string to extract the command and its arguments.

        Arguments are separated by white spaces. Anything within single quotes,
        including spaces and backlashes, is interpreted literally. Anything within
        double quotes is interpreted literally, except for backlashes which escape
        some characters. Outside quotes, backlashes escape any character."""
        listArgs = []
        currentArg = ""
        isBetweenSingleQuotes = False
        isBetweenDoubleQuotes = False
        escapeNextChar = False
        for iChar, char in enumerate(inputString):
            if escapeNextChar:
                if isBetweenDoubleQuotes:
                    if char in ['"', "\\", "$", "`"]:
                        currentArg = currentArg + char
                    else:
                        currentArg = currentArg + "\\" + char
                else:
                    currentArg = currentArg + char
                escapeNextChar = False
            else:
                match char:
                    case "\\":
                        if isBetweenSingleQuotes:
                            currentArg = currentArg + char
                        else:
                            escapeNextChar = True
                    case "'":
                        currentArg, isBetweenSingleQuotes = self.interpretArgQuote(
                            char,
                            isBetweenSingleQuotes,
                            isBetweenDoubleQuotes,
                            currentArg,
                            iChar,
                            inputString,
                        )
                    case '"':
                        currentArg, isBetweenDoubleQuotes = self.interpretArgQuote(
                            char,
                            isBetweenDoubleQuotes,
                            isBetweenSingleQuotes,
                            currentArg,
                            iChar,
                            inputString,
                        )
                    case " ":
                        if isBetweenSingleQuotes or isBetweenDoubleQuotes:
                            currentArg = currentArg + char
                        else:
                            # Start new block delimited by a space
                            if len(currentArg) > 0:
                                listArgs.append(currentArg)
                                currentArg = ""
                    case _:
                        currentArg = currentArg + char
        if len(currentArg) > 0:
            listArgs.append(currentArg)
        return listArgs

    def interpretArgQuote(
        self,
        quoteType: str,
        isBetweenTargetQuoteType: bool,
        isBetweenOtherQuoteType: bool,
        currentParam: str,
        iChar: int,
        inputParamsString: str,
    ) -> tuple[str, bool]:
        """Util function called when a quote is encountered in the arguments."""
        # Ignore if this is a pair of empty quotes
        if (iChar < (len(inputParamsString) - 1) and inputParamsString[iChar + 1] == quoteType) or (
            iChar > 0 and inputParamsString[iChar - 1] == quoteType
        ):
            return currentParam, isBetweenTargetQuoteType
        # Interpret literaly if this is embedded in another quote block or not a pair of quotes
        if isBetweenOtherQuoteType or (
            not isBetweenTargetQuoteType
            and (iChar == len(inputParamsString) - 1 or quoteType not in inputParamsString[iChar + 1 :])
        ):
            currentParam = currentParam + quoteType
            return currentParam, isBetweenTargetQuoteType
        # Enter a new quote block
        isBetweenTargetQuoteType = not isBetweenTargetQuoteType
        return currentParam, isBetweenTargetQuoteType

    def isValid(self) -> bool:
        """By default, all commands are valid."""
        return True

    @classmethod
    def getBuiltinCommandNames(cls) -> list[str]:
        """Returns the name of all child builtin classes."""
        lenParentCommandName = len(cls.__name__)
        listChildrenCommandName = [child.__name__ for child in cls.__subclasses__()]
        # Clean subclasses name
        for iChild in range(len(listChildrenCommandName)):
            listChildrenCommandName[iChild] = listChildrenCommandName[iChild][:-lenParentCommandName].lower()
        # Only keep builtin classes
        listChildrenCommandName.remove("custom")
        return listChildrenCommandName


class CustomCommand(Command):
    def isValid(self) -> bool:
        """Checks that the custom command exists and can be executed."""
        if not shutil.which(self.command, mode=os.X_OK):
            sys.stdout.write(f"{self.command}: command not found\n")
            return False
        else:
            return True

    def execute(self):
        """Runs the custom command."""
        output = subprocess.run([self.command] + self.args, capture_output=True, text=True)
        return output.stdout


class ExitCommand(Command):
    def isValid(self) -> bool:
        """Checks arguments of the command."""
        if len(self.args) > 1 or self.args[0] not in ["0", "1"]:
            sys.stdout.write("exit: expects only 0 or 1\n")
            return False
        else:
            return True

    def execute(self) -> None:
        """Closes the shell."""
        self.parseNextCommand = False


class EchoCommand(Command):
    def execute(self) -> str:
        """Displays the arguments."""
        return f"{' '.join(self.args)}\n"


class TypeCommand(Command):
    def isValid(self):
        """Checks that only one argument is provided."""
        if len(self.args) > 1:
            sys.stdout.write("type: expects only one parameter\n")
            return False
        else:
            return True

    def execute(self):
        """Displays the type or location of the command passed in argument."""
        if self.args[0] in Command.getBuiltinCommandNames():
            return f"{self.args[0]} is a shell builtin\n"
        else:
            executablePath = shutil.which(self.args[0], mode=os.X_OK)
            if executablePath:
                return f"{self.args[0]} is {executablePath}\n"
            else:
                return f"{self.args[0]}: not found\n"


class PwdCommand(Command):
    def isValid(self):
        """Checks that no argument is provided."""
        if len(self.args) > 0:
            sys.stdout.write("pwd: expects no parameter\n")
            return False
        else:
            return True

    def execute(self):
        """Displays the current working directory."""
        return f"{os.getcwd()}\n"


class CdCommand(Command):
    def isValid(self):
        """Checks that only one argument is provided."""
        if len(self.args) > 1:
            sys.stdout.write("type: expects only one parameter\n")
            return False
        else:
            return True

    def execute(self) -> None | str:
        """Changes working directory to a target path (absolute, relative, or HOME)."""
        if self.args[0] == "~":
            os.chdir(os.environ["HOME"])
        elif os.path.isdir(self.args[0]):
            os.chdir(self.args[0])
        else:
            return f"cd: {self.args[0]}: No such file or directory\n"
