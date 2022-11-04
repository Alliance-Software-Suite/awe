import argparse as ap
import os


def get_args():
    parser = ap.ArgumentParser(description="AWE: Audit With Ease")
    parser.add_help = True
    parser.add_argument(
        "-n",
        "--nation",
        metavar="ID",
        type=int,
        dest="nations",
        help="ID of nation(s) to audit. If auditing multiple nations, use this argument multiple times. "
        "Do NOT use with -n/--nation",
        action="append",
    )
    parser.add_argument(
        "-a",
        "--alliance",
        metavar="ID",
        type=int,
        dest="alliances",
        help="ID of alliance(s) to audit. If auditing multiple alliances, use this argument multiple times. "
        "Do NOT use with -n/--nation",
        action="append",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        type=str,
        default=os.devnull,
        help="Path to config file. Use the config file for more advanced features. "
        "Values in the config file will be overwritten by command line arguments.",
    )
    parser.add_argument("-k", "--key", type=str, help="Provide the API key to be used.")
    parser.add_argument(
        "-m",
        "--military",
        metavar="MMR",
        type=str,
        dest="mmr",
        help="Sets MMR and enables military auditing.",
    )
    parser.add_argument(
        "-i",
        "--infra",
        metavar="MAX",
        type=int,
        help="Enables infrastructure auditing and sets the maximum infra allowed. "
        "Use the config file to automatically set this value based on the nation's city count.",
    )
    parser.add_argument(
        "-l",
        "--land",
        metavar="MIN",
        type=int,
        help="Enables land auditing and sets the minimum land allowed. "
        "Use the config file to automatically set this value based on the nation's city count.",
    )

    args = parser.parse_args()

    return args
