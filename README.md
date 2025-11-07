# Mini shell

This project is a minimal shell implemented in Python 3.12, developed by following the ["Build Your Own Shell" Challenge](https://app.codecrafters.io/courses/shell/overview). The challenge provides the base architecture and a sequence of validation steps through an automated testing system.

To run on **Windows**:

```bash
py app/main.py
```

## Usage

### Builtin commands

The shell implements several builtin commands:
- `exit 0`: exists the shell (terminates with status 0).
- `echo`: displays the given arguments.
```bash
$ echo Hello world
Hello world
```
- `type`: identifies whether a command is builtin or external and shows its location if applicable.
```bash
$ type echo
echo is a shell builtin
```
```bash
$ type ls
ls is C:\Program Files\Git\usr\bin\ls.EXE
```
- `pwd`: displays the current working directory.
- `cd`: changes the current working directory.
- `history`: lists previously executed commands. Example:
```bash
$ echo Hello World
Hello World
$ pwd
/usr/local/bin
$ cd ../
$ pwd
/usr/local/
$ history
   1  echo Hello World
   2  pwd
   3  cd ../
   4  pwd
   5  history
```
The shell reads from and writes to `app/history.txt` so that command history persists between sessions.

### Non-builtins

Commands that are **not builtin** are resolved using the system’s `PATH` and executed if an appropriate executable is found. Example:

```bash
$ ls
Pipfile
Pipfile.lock
README.md
app
codecrafters.yml
your_program.sh
```

### Quoting and escaping

This shell supports single quotes, double quotes, and escaped characters. Example:

```bash
$ ec''ho "Hi   " \ \ I'm "\"Juliette\""
Hi      I'm "Juliette"
```

### Redirection

Command output and error can be redirected to files using `>` (or `1>`) and `2>`, respectively. Examples:
```bash
$ echo Hi > usr/local/bin/hi.txt
$ echho Hi 2> usr/local/bin/error.txt
```
`>` (and `1>`, `2>`) overwrites the target file if it exists, whereas `>>` (and `1>>`, `2>>`) appends to the target file.

### Interactive inputs

- Press `TAB` to autocomplete the current command.
- Use the `UP` and `DOWN` arrow keys to navigate through the command history.

### Pipelines

Pipelines (`|`) are currently **beyond the project’s scope**.
