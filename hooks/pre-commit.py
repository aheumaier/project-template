#!/usr/bin/env python
import os
import errno
import subprocess
import re


def decode_color(color):
    """Decode color string in terminal colors"""
    if color == "red":
        return " \033[31;1mERROR\033[31;1;1m {}\033[0m"
    elif color == "yellow":
        return " \033[33;1m*\033[33;1;1m {}\033[0m"
    elif color == "green":
        return " \033[32;1mOK\033[32;1;1m {}\033[0m"
    else:
        return ""


def formatted_message(message, color):
    """Format and colorize print() output"""
    print(decode_color(color) .format(message))


def local_branch():
    """Return the current git granch"""
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, check=True)
    return branch.stdout


def changed_files(filter=""):
    """ Get the git index and filter on returned list"""
    diff = subprocess.run(["git", "diff", "--cached", "--name-only",
                           "--diff-filter=ACM", "--relative"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, check=True)
    pattern = re.compile(filter)
    return [k for k in diff.stdout.split('\n') if pattern.match(k)]


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    if which(name) is None:
        exit(formatted_message(f"ERROR: {name} command not found", "red"))


def branch_naming_policies():
    formatted_message("Running branch naming policies...", "yellow")
    developers = "gubilgut|anheumai|oscheer|dparys|pkirch|daheinze|rthan|trunk|mbeck|tgoerg|kkraus|marendt"
    branch_prefixes = "feature|fix|build|chore|ci|docs|style|refactor|perf|test"
    valid_branch_regex = re.compile(f"^({branch_prefixes})/({developers})-[0-9][0-9][0-9][0-9][0-9]-[a-zA-Z0-9._-]+$")
    message = "Branch names in this project must adhere to this contract: {}. \n\nYour commit will be rejected. You should rename your branch to a valid name and try again.\n" .format(
        valid_branch_regex)
    if not valid_branch_regex.match(local_branch()):
        formatted_message(message, "red")
        exit(1)
    formatted_message(" ", "green")
    return True


def shellcheck():
    changed_shell_files = changed_files(r".*\.sh$")
    if changed_shell_files:
        formatted_message("Running shellcheck...", "yellow")
        try:
            result = subprocess.run(["shellcheck", "-x", "-a", " ".join(changed_shell_files)],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True)
            if result.returncode == 0:
                formatted_message(" ", "green")
                return True
            else:
                print(result.stdout)
                exit(formatted_message("shellcheck disapproves of your changes", "red"))
        except OSError as e:
            if e.errno == errno.ENOENT:
                print("")
                exit(formatted_message("shellcheck command not found", "red"))
            else:
                # Something else went wrong while trying to run `shellcheck`
                raise
    formatted_message("Skipping shellcheck", "yellow")


def markdownlint():
    changed_shell_files = changed_files(r".*\.md$")
    if changed_shell_files:
        formatted_message("Running markdownlint...", "yellow")
        try:
            result = subprocess.run(["npx", "markdownlint", " ".join(changed_shell_files)],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True)
            if result.returncode == 0:
                formatted_message(" ", "green")
                return True
            else:
                print(result.stdout)
                exit(formatted_message("markdownlint disapproves of your changes", "red"))
        except OSError as e:
            if e.errno == errno.ENOENT:
                exit(formatted_message("markdownlint command not found", "red"))
            else:
                # Something else went wrong while trying to run `markdownlint`
                raise
    formatted_message("Skipping markdownlint", "yellow")


def run_flake8():
    formatted_message("Running flake8...", "yellow")
    from flake8.api import legacy as flake8
    style_guide = flake8.get_style_guide(ignore=['H101','H301','H306','H401',
    'E402','H403','H404','H405']
                                         )
    report = style_guide.check_files(["."])
    assert report.total_errors == 0, '\033[31;1mERROR\033[31;1;1m Flake8 found errors\033[0m' 
    

def run_pytest():
    formatted_message("Running tox on pytest-lib...", "yellow")
    import tox
    import sys
    toxargs = ["-e", "pytest-lib"]
    errno = tox.cmdline(toxargs)
    sys.exit(errno)
    # assert pytest.main(['-vv', '-n 8', '-x', 'tests/tools']) == 0, '\033[31;1mERROR\033[31;1;1m Pytest found errors\033[0m"'


def python_testing():
    changed_py_files = True #changed_files(r".*\.py$")
    if changed_py_files:
        run_flake8()
        run_pytest()
        return 0
    formatted_message("Skipping python_testing", "yellow")


if __name__ == "__main__":
    is_tool("npx")
    branch_naming_policies()
    shellcheck()
    markdownlint()
    python_testing()
