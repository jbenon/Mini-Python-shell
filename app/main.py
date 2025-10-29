import sys


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
        match command:
            case "exit":
                param = int(commandParsed[1])
            case "echo":
                param = commandParsed[1:]
            case _:
                isCommandInvalid = True

        # Exit
        if command == "exit" and param == 0:
            exit = True

        # Echo
        if command == "echo":
            sys.stdout.write(f"{' '.join(param)}\n")

        # Invalid
        if isCommandInvalid:
            sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
