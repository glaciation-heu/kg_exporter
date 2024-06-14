import signal
import sys

from app.kgexporter_context_builder import KGExporterContextBuilder


def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    builder = KGExporterContextBuilder(sys.argv[1:])
    context = builder.build()
    context.start()
    context.wait_for_termination()


if __name__ == "__main__":
    main()