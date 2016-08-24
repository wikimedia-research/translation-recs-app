import pytest
import itertools

from recommendation.api import utils


@pytest.mark.parametrize('arg_count', range(1, 10))
def test_threading_function_arg_handling(arg_count):
    def to_thread(*args):
        if arg_count != len(args):
            raise Exception()
        return [sum(args)]
    with pytest.raises(Exception):
        to_thread(*range(arg_count + 1))
    args = [(arg_count * i,) * arg_count for i in range(100)]
    result = utils.thread_function(to_thread, args)
    combined_result = list(itertools.chain.from_iterable(result))
    assert [arg_count ** 2 * i for i in range(100)] == combined_result
