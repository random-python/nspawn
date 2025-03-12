
def define_parser():
    import argparse
    parser = argparse.ArgumentParser(
        prog='main',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(
        title="required commands",
        help='Select one of:',
    )    
    command_list = commands.add_parser(
        'list',
        help='List included services',
    )
    command_ensure = commands.add_parser(
        'ensure',
        help='Provision included service',
    )
    command_ensure.add_argument(
        "service",
        help='Service name',
    )
    import textwrap
    parser.epilog = textwrap.dedent(
        f"""\
        commands usage:\n
        {command_list.format_usage()}
        {command_ensure.format_usage()}
        """
    )
    return parser

parser = define_parser()

parser.print_help()
