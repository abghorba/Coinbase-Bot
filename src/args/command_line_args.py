import argparse

parser = argparse.ArgumentParser(description="Method of collecting user order")
group = parser.add_mutually_exclusive_group()
group.add_argument("--cli", help="Place orders via command line input?", action="store_true")
group.add_argument("--yaml", help="Place orders via YAML file?", action="store_true")


def get_command_line_args(verbose=False):
    """
    Returns a dictionary of command line arguments.

    :param verbose: True to print the CLI args
    :return: None
    """

    cli_args = vars(parser.parse_args())

    if verbose:
        print(cli_args)

    return cli_args
