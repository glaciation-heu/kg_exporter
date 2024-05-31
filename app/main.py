import argparse
import logging
import signal


def main() -> None:
    parser = argparse.ArgumentParser(description="Kubernetes watcher service")
    parser.add_argument(
        "--incluster",
        dest="incluster",
        action="store_true",
        help="Load a Kubernetes config from within a cluster",
    )
    args = parser.parse_args()
    print(args)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)


if __name__ == "__main__":
    main()
