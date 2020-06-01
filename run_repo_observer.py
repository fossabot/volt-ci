import argparse

from ci.repo_observer.observer import observer


def run_observer():
    """
    Run Observer
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dispatcher-server",
        help="dispatcher host:port , by default it uses localhost:8000",
        default="localhost:8000",
        action="store",
    )
    parser.add_argument(
        "--repo", metavar="REPO", type=str, help="path to the repository to observe"
    )
    parser.add_argument(
        "--poll", help="how long to keep polling repository", default=5, type=int
    )
    parser.add_argument(
        "--branch", help="which branch to run tests against", default="master", type=str
    )

    args = parser.parse_args()
    dispatcher_host, dispatcher_port = args.dispatcher_server.split(":")

    observer(dispatcher_host, dispatcher_port, args.repo, args.poll, args.branch)


if __name__ == "__main__":
    run_observer()
