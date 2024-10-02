import cProfile
import pstats
from io import StringIO
from collections import namedtuple

class ProfilerLens:

    _SORT_OPTIONS = namedtuple('_SORT_OPTIONS', ['CALLS', 'CUMULATIVE', 'TIME', 'FILENAME'])
    SORT_OPTIONS = _SORT_OPTIONS(
        CALLS='calls',
        CUMULATIVE='cumulative',
        TIME='time',
        FILENAME='filename'
    )
    def __init__(self, sort_by=SORT_OPTIONS.CUMULATIVE):
        self.profiler = cProfile.Profile()
        self.sort_by = sort_by

    def __enter__(self):
        self.profiler.enable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.disable()
        self._print_stats(self.profiler, self.sort_by)

    @staticmethod
    def profile_code(sort_by=SORT_OPTIONS.CUMULATIVE, save_to_file=False, filename='profiling_results.prof'):
        def decorator(func):
            def wrapper(*args, **kwargs):
                profiler = cProfile.Profile()
                profiler.enable()
                result = func(*args, **kwargs)
                profiler.disable()
                ProfilerLens._print_stats(profiler, sort_by, save_to_file, filename)
                return result
            return wrapper
        return decorator

    @staticmethod
    def _print_stats(profiler, sort_by, save_to_file=False, filename='profiling_results.prof'):
        if save_to_file:
            profiler.dump_stats(filename)
            print(f"Profile data saved to {filename}")

        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats(sort_by)
        ps.print_stats()
        print(s.getvalue())

# Example usage
@ProfilerLens.profile_code(save_to_file=True)
def example_function():
    total = 0
    for i in range(100):
        total += i
    return total

if __name__ == '__main__':
    for i in range(10):
        example_function()
