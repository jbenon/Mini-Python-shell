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
        match len(command_parsed):
            case 1:
                param = None
            case 2:
                param = int(command_parsed[1])

        # Exit or invalid
        if command == "exit" and param == 0:
            exit = True
        else:
            sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
