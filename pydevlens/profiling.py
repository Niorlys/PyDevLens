import cProfile
import pstats
from io import StringIO

def profile_code(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())
        return result
    return wrapper

# Example usage
@profile_code
def example_function():
    total = 0
    for i in range(100):
        total += i
    return total

if __name__ == '__main__':
    for i in range(10):
        example_function()
