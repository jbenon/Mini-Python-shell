import sys
import os
import shutil
import subprocess


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

        # Process command parameters
        isCommandInvalid = False
        match command:
            case "exit":
                if len(commandParsed) > 1:
                    param = int(commandParsed[1])
                else:
                    isCommandInvalid = True
            case "echo":
                if len(commandParsed) > 1:
                    param = commandParsed[1:]
                else:
                    isCommandInvalid = True
            case "type":
                if len(commandParsed) > 1:
                    param = commandParsed[1]
                else:
                    isCommandInvalid = True
            case _:
                executablePath = shutil.which(command, mode=os.X_OK)
                if not executablePath:
                    isCommandInvalid = True

        # Invalid
        if isCommandInvalid:
            sys.stdout.write(f"{command}: command not found\n")
            continue

        # Exit
        if command == "exit" and param == 0:
            exit = True
            continue

        # Echo
        if command == "echo":
            sys.stdout.write(f"{' '.join(param)}\n")
            continue

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
            continue

        # Executable file
        subprocess.run(commandParsed)


if __name__ == "__main__":
    main()
