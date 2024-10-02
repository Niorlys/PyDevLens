import sys
import time
import logging
import inspect
from collections import namedtuple
from functools import wraps
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class Tracer:
    _EVENT_NAMES = namedtuple("_EVENT_NAMES", ["CALL", "RETURN", "EXCEPTION", "LINE"])
    EVENTS = _EVENT_NAMES(
        CALL="call", RETURN="return", EXCEPTION="exception", LINE="line"
    )
    
    # Methods that should not be traced
    _NON_TRACEABLE_METHODS = {"start_trace", "stop_trace","__enter__","__exit__"}

    def __init__(self, log_level=logging.INFO):
        self.trace_data = []
        logging.getLogger().setLevel(log_level)

    def start_trace(self):
        sys.settrace(self.trace_calls)

    def stop_trace(self):
        sys.settrace(None)

    def __enter__(self):
        self.start_trace()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_trace()
        if exc_type:
            logging.error(f"Exception occurred: {exc_val}")
            traceback.print_exception(exc_type, exc_val, exc_tb)

    def trace_calls(self, frame, event, arg):
        func_name = frame.f_code.co_name
        module_name = frame.f_globals.get("__name__", "unknown")

        if func_name in self._NON_TRACEABLE_METHODS:
            return None

        if event == self.EVENTS.CALL:
            self._log_function_entry(func_name, module_name, frame)

        elif event == self.EVENTS.RETURN:
            self._log_function_exit(func_name, module_name)

        elif event == self.EVENTS.EXCEPTION:
            self._log_exception(func_name, module_name)

        return self.trace_calls

    def trace(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            module_name = func.__module__

            # Log function entry
            self._log_function_entry(func_name, module_name, None, args, kwargs)

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logging.info(
                    f"Exited function: {func_name} in module: {module_name} "
                    f"with return value: {result!r} (Execution time: {execution_time:.4f} seconds)"
                )
                return result
            except Exception as e:
                self._log_exception(func_name, module_name, e)
                raise
        return wrapper

    def _log_function_entry(self, func_name, module_name, frame=None, args=None, kwargs=None):
        if frame is not None:
            args, _, _, values = inspect.getargvalues(frame)
            arg_str = ", ".join(f"{arg}={values[arg]}" for arg in args)
        else:
            args_repr = [repr(a) for a in args] if args else []
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()] if kwargs else []
            arg_str = ", ".join(args_repr + kwargs_repr)

        logging.info(f"Calling function: {func_name} in module: {module_name} with arguments: ({arg_str})")

    def _log_function_exit(self, func_name, module_name):
        logging.info(f"Exited function: {func_name} in module: {module_name}")

    def _log_exception(self, func_name, module_name, exception=None):
        if exception is None:
            logging.warning(f"Exception in function: {func_name} in module: {module_name}")
        else:
            error_message = f"Exception in function: {func_name} in module: {module_name} with error: {str(exception)}"
            logging.error(error_message)
            logging.error(traceback.format_exc())



# Example usage
if __name__ == "__main__":

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

    with Tracer() as tracer:
        test_func(5, 10, z=15)
