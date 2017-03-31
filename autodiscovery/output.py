import click


class AbstractOutput(object):
    def send(self, message, error=False):
        raise NotImplementedError("Class {} must implement method 'send'".format(type(self)))


class EmptyOutput(AbstractOutput):
    def send(self, message, error=False):
        pass


class ConsoleOutput(AbstractOutput):
    def send(self, message, error=False):
        fg = "red" if error else "green"
        click.secho(message, fg=fg)
