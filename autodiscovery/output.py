import click
from colorama import Fore

from tqdm import tqdm


class AbstractOutput(object):
    def send(self, message, error=False):
        raise NotImplementedError(f"Class {type(self)} must implement method 'send'")


class EmptyOutput(AbstractOutput):
    def send(self, message, error=False):
        pass


class ConsoleOutput(AbstractOutput):
    def send(self, message, error=False):
        fg = "red" if error else "green"
        click.secho(message, fg=fg)


class TqdmOutput(AbstractOutput):
    def send(self, message, error=False):
        color = Fore.RED if error else Fore.GREEN
        tqdm.write(f"{color}{message}")
