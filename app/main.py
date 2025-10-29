import sys


def main():
    # Print a prompt
    sys.stdout.write("$ ")

    # Handle invalid commands
    command = input()
    sys.stdout.write(f"{command}: command not found")


if __name__ == "__main__":
    main()
