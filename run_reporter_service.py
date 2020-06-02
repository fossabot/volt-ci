import argparse
from ci.reporter import reporter_service


def run_reporter():
    """
    Entry point to reporter service
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="Reporter's host, defaults to localhost",
        default="localhost",
        action="store",
    )
    parser.add_argument(
        "--port",
        help="Reporter's port, defaults to 8555",
        default=8555,
        action="store",
    )

    args = parser.parse_args()

    reporter_service(args.host, int(args.port))


if __name__ == "__main__":
    run_reporter()
