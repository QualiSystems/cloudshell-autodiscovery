import click
from colorama import Fore


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


class TqdmProgressBarOutput(AbstractOutput):
    def __init__(self, progress_bar):
        """

        :param tqdm.std.tqdm progress_bar:
        """
        self._progress_bar = progress_bar

    def send(self, message, error=False):
        color = Fore.RED if error else Fore.GREEN
        self._progress_bar.set_description(f"{color}{message}")
