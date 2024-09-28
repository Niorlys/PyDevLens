import sys
import time
import logging
import inspect
from collections import namedtuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class Tracer:
    # Define a named tuple for event types
    _EVENT_NAMES = namedtuple("_EVENT_NAMES", ["CALL", "RETURN", "EXCEPTION", "LINE"])
    EVENTS = _EVENT_NAMES(
        CALL="call", RETURN="return", EXCEPTION="exception", LINE="line"
    )
    _NON_TRACEABLE_METHODS = ("start_trace", "stop_trace")

    def __init__(self):
        self.trace_data = []

    def start_trace(self):
        sys.settrace(self.trace_calls)

    def stop_trace(self):
        sys.settrace(None)

    def trace_calls(self, frame, event, arg):
        func_name = frame.f_code.co_name
        module_name = frame.f_globals.get("__name__", "unknown")
        if func_name in self._NON_TRACEABLE_METHODS:
            return None

        if event == self.EVENTS.CALL:
            # Extract arguments using inspect
            args, _, _, values = inspect.getargvalues(frame)
            arg_str = ", ".join(f"{arg}={values[arg]}" for arg in args)

            self.trace_data.append(
                (func_name, module_name, time.time(), self.EVENTS.CALL, arg_str)
            )
            logging.info(
                f"Calling function: {func_name} in module: {module_name} with arguments: ({arg_str})"
            )
        elif event == self.EVENTS.RETURN:
            self.trace_data.append(
                (func_name, module_name, time.time(), self.EVENTS.RETURN)
            )
            logging.info(f"Exited function: {func_name} in module: {module_name}")

        elif event == self.EVENTS.EXCEPTION:
            logging.warning(
                f"Exception in function: {func_name} in module: {module_name}"
            )

        return self.trace_calls


# Example usage
if __name__ == "__main__":
    tracer = Tracer()
    tracer.start_trace()

    # Some test function with arguments
    def f(arg):
        print(arg)
        print("ajajaja")

    def g(arg):
        print(arg)

    def h(arg):
        f(arg)
        g(arg)
        print(arg)

    def test_func(x, y, z=10):
        f(123)
        g(456)
        h(789)
        return x + y + z

    test_func(5, 10, z=15)

    tracer.stop_trace()
