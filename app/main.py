import sys


def main():
    exit = False
    while not exit:
        # Print a prompt
        sys.stdout.write("$ ")

        # Parse command
        command = input()
        command_parsed = command.split(" ")
        command = command_parsed[0]

        # Process command parameters
        match command:
            case "exit":
                param = int(command_parsed[1])
            case "echo":
                param = command_parsed[1:]
            case _:
                command = "invalid"

        # Exit
        if command == "exit" and param == 0:
            exit = True

        # Echo
        if command == "echo":
            sys.stdout.write(f"{' '.join(param)}\n")

        # Invalid
        if command == "invalid":
            sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
