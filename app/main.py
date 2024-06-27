import signal
import sys

from app.kgexporter_context_builder import KGExporterContextBuilder


def main() -> None:
    builder = KGExporterContextBuilder.from_args(sys.argv[1:])
    if builder:
        context = builder.build()

        signal.signal(signal.SIGINT, context.exit_gracefully)
        signal.signal(signal.SIGTERM, context.exit_gracefully)

        context.start()
        context.wait_for_termination()


if __name__ == "__main__":
    main()
