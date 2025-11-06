import os
import shutil
import subprocess


def parseInputIntoCommand(inputString: str = "") -> list[str]:
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
                    currentArg, isBetweenSingleQuotes = interpretArgQuote(
                        char,
                        isBetweenSingleQuotes,
                        isBetweenDoubleQuotes,
                        currentArg,
                        iChar,
                        inputString,
                    )
                case '"':
                    currentArg, isBetweenDoubleQuotes = interpretArgQuote(
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


class Command:
    # History is a class attribute
    history = []

    def __init__(self, listArgs: list[str] = []):
        # By default, keep looking for other commands
        self.parseNextCommand = True

        # Parse the command and its arguments
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
        self.appendOutput = False
        self.fileError = ""
        self.appendError = False
        for iArg in range(len(self.args) - 1):
            if self.args[iArg] == ">" or self.args[iArg] == "1>":  # stdout
                self.fileOutput = self.args[iArg + 1]
                self.args.pop(iArg)
                self.args.pop(iArg)
        for iArg in range(len(self.args) - 1):
            if self.args[iArg] == ">>" or self.args[iArg] == "1>>":  # stdout append
                self.fileOutput = self.args[iArg + 1]
                self.args.pop(iArg)
                self.args.pop(iArg)
                self.appendOutput = True
        for iArg in range(len(self.args) - 1):
            if self.args[iArg] == "2>":  # stderr
                self.fileError = self.args[iArg + 1]
                self.args.pop(iArg)
                self.args.pop(iArg)
        for iArg in range(len(self.args) - 1):
            if self.args[iArg] == "2>>":  # stderr append
                self.fileError = self.args[iArg + 1]
                self.args.pop(iArg)
                self.args.pop(iArg)
                self.appendError = True

    def isValid(self) -> None:
        """By default, all commands are valid."""
        return

    def updateHistory(self) -> None:
        """Adds the current command to the list of previous commands."""
        if len(self.args) > 0:
            self.__class__.history.append(f"{self.command} {' '.join(self.args)}")
        else:
            self.__class__.history.append(f"{self.command}")

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
    def isValid(self) -> str | None:
        """Checks that the custom command exists and can be executed."""
        if not shutil.which(self.command, mode=os.X_OK):
            return f"{self.command}: command not found\n"

    def execute(self):
        """Runs the custom command."""
        output = subprocess.run([self.command] + self.args, capture_output=True, text=True)
        return output.stdout, output.stderr


class ExitCommand(Command):
    def isValid(self) -> str | None:
        """Check thet only one argument, equal to 0 or 1, is provided."""
        if len(self.args) > 1 or self.args[0] not in ["0", "1"]:
            return "exit: expects only 0 or 1\n"

    def execute(self) -> None:
        """Closes the shell."""
        self.parseNextCommand = False


class EchoCommand(Command):
    def execute(self) -> str:
        """Displays the arguments."""
        return f"{' '.join(self.args)}\n"


class TypeCommand(Command):
    def isValid(self) -> str | None:
        """Checks that only one argument is provided."""
        if len(self.args) > 1:
            return "type: expects only one parameter\n"

    def execute(self) -> str:
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
    def isValid(self) -> str | None:
        """Checks that no argument is provided."""
        if len(self.args) > 0:
            return "pwd: expects no parameter\n"

    def execute(self) -> str:
        """Displays the current working directory."""
        return f"{os.getcwd()}\n"


class CdCommand(Command):
    def isValid(self) -> str | None:
        """Checks that only one argument is provided."""
        if len(self.args) > 1:
            return "type: expects only one parameter\n"

    def execute(self) -> None | str:
        """Changes working directory to a target path (absolute, relative, or HOME)."""
        if self.args[0] == "~":
            os.chdir(os.environ["HOME"])
        elif os.path.isdir(self.args[0]):
            os.chdir(self.args[0])
        else:
            return f"cd: {self.args[0]}: No such file or directory\n"


class HistoryCommand(Command):
    def isValid(self) -> str | None:
        """Checks possible history arguments, either empty, number or with -r."""
        if len(self.args) > 2:
            return "history: expects two parameters maximum\n"
        if len(self.args) > 1:  # history -r path
            if self.args[0] not in ["-r", "-w", "-a"]:
                return "history: first argument should be -r, -w or -a\n"
        elif len(self.args) > 0:
            try:
                int(self.args[0])
            except ValueError:
                return "history: expects an int as parameter\n"
            if int(self.args[0]) > len(self.__class__.history):
                return f"history: parameter must be inferior or equal to {len(self.__class__.history)}\n"

    def execute(self) -> str | None:
        """Displays the list of previous commands or modifies history file's contents."""
        # Modifies history file's contents
        if len(self.args) > 1:
            match self.args[0]:
                case "-r":  # Append the content of the history file to current history
                    self.nStartFileHistoryLines = 0
                    with open(self.args[1], "r") as fileHistory:
                        for lineHistory in fileHistory:
                            self.__class__.history.append(lineHistory.rstrip())
                            self.nStartFileHistoryLines += 1
                case "-w":  # Write the current history to a history file and delete current history
                    with open(self.args[1], "w") as fileHistory:
                        for lineHistory in self.__class__.history:
                            fileHistory.write(f"{lineHistory}\n")
                    self.__class__.history.clear()
                case "-a":  # Write new lines only to a history file and delete current history
                    countLines = 0
                    if not hasattr(self, "nStartFileHistoryLines"):
                        self.nStartFileHistoryLines = 0
                    with open(self.args[1], "a") as fileHistory:
                        for lineHistory in self.__class__.history:
                            if countLines < self.nStartFileHistoryLines:
                                continue
                            fileHistory.write(f"{lineHistory}\n")
                    self.__class__.history.clear()
                    self.nStartFileHistoryLines = 0

        # Display history
        else:
            listHistory = ""
            if self.args == []:
                self.args = [len(self.__class__.history)]
            self.args[0] = int(self.args[0])
            for iCommand, command in enumerate(self.__class__.history):
                if iCommand < len(self.__class__.history) - self.args[0]:
                    continue
                listHistory = listHistory + f"\t{iCommand + 1}  {command}\n"
            return listHistory
