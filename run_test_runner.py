"""
Script to run test runner
"""
import argparse

from ci.test_runner import test_runner_server


def run_test_runner():
    range_start = 8900
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="runner's host, by default it uses localhost",
        default="localhost",
        action="store",
    )
    parser.add_argument(
        "--port",
        help=f"runner's port, by default it uses values >={range_start}",
        action="store",
    )
    parser.add_argument(
        "--dispatcher-server",
        help="dispatcher host:port, by default it uses localhost:8000",
        default="localhost:8000",
        action="store",
    )
    parser.add_argument(
        "--repo",
        metavar="REPO",
        type=str,
        help="path to the repository this will observe",
    )

    args = parser.parse_args()

    runner_host = args.host
    runner_port = args.port
    repository = args.repo
    dispatcher_host, dispatcher_port = args.dispatcher_server.split(":")

    test_runner_server(
        runner_host, runner_port, repository, dispatcher_host, dispatcher_port
    )


if __name__ == "__main__":
    run_test_runner()
