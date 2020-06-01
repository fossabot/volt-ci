import argparse
from ci.dispatcher.dispatcher import dispatcher


def run_dispatcher():
    """
    Entry point to dispatch server
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="Dispatchers host, defaults to localhost",
        default="localhost",
        action="store",
    )
    parser.add_argument(
        "--port",
        help="Dispatchers port, defaults to 8000",
        default=8000,
        action="store",
    )

    args = parser.parse_args()

    dispatcher(args.host, int(args.port))


if __name__ == "__main__":
    run_dispatcher()
