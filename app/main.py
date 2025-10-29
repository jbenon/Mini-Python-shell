import sys
import os
import shutil


def main():
    exit = False
    isCommandInvalid = False
    while not exit:
        # Print a prompt
        sys.stdout.write("$ ")

        # Parse command
        command = input()
        commandParsed = command.split(" ")
        command = commandParsed[0]

        print(os.environ["PATH"])

        # Process command parameters
        isCommandInvalid = False
        match command:
            case "exit":
                param = int(commandParsed[1])
            case "echo":
                param = commandParsed[1:]
            case "type":
                param = commandParsed[1]
            case _:
                isCommandInvalid = True

        # Exit
        if command == "exit" and param == 0:
            exit = True

        # Echo
        if command == "echo":
            sys.stdout.write(f"{' '.join(param)}\n")

        # Type
        if command == "type":
            if param in ["exit", "echo", "type"]:
                sys.stdout.write(f"{param} is a shell builtin\n")
            else:
                # Search for command in PATH
                executablePath = shutil.which(param, mode=os.X_OK)
                if executablePath:
                    sys.stdout.write(f"{param} is {executablePath}\n")
                else:
                    sys.stdout.write(f"{param}: not found\n")

        # Invalid
        if isCommandInvalid:
            sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
