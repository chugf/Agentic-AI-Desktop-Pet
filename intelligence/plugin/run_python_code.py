import io
import sys


def run_python_code(source_code: str):
    """
    当你想运行Python源代码时非常有用
    """
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    try:
        sys.stdout = captured_output
        exec(source_code)
        output = captured_output.getvalue()
    finally:
        sys.stdout = original_stdout

    return output
