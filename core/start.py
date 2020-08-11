import multiprocessing
from os import path

from androguard.misc import AnalyzeAPK
from androguard.session import Save, Load, Session


def load_androguard(file_path, force_reload=False, write_session=True, session_file=None, s=None):
    """
    Should handle saving and loading sessions automatically.

    Writing and Loading sessions currently cause a Kernel Disconnect or an EOF Error (Pickle serialization issues)
    """
    if (not force_reload) and path.exists(session_file):
        print("Loading Existing Session")
        s = Load(session_file)
        a = d = dx = None
    else:
        print("Loading Session from Apk at", file_path)
        if s is None:
            s = Session()
        a, d, dx = AnalyzeAPK(file_path, s)
        if write_session:
            print("Saving Loaded Session to", session_file)
            s.add(file_path, dx=dx)
            Save(s, session_file)
    return a, d, dx


def process_files(apk1, apk2, should_multiprocess=True):
    """
    Similar issues to load_androguard. Serialization issue prevents sending this object (multiple Gbs in RAM) through a
    multiprocessing mechanism such as Pipes (or anything build on top of it, i. e. Queues).
    """
    file_paths = (apk1, apk2)
    if not should_multiprocess:
        s = Session()
        return tuple(map(lambda f: load_androguard(f, True, False, s=s), file_paths))

    parent_conn, child_conn = multiprocessing.Pipe(False)

    def post_result(file_path, conn):
        value = load_androguard(file_path, True, False)
        conn.send((file_path, value))

    ps = [multiprocessing.Process(target=post_result, args=(f, child_conn)) for f in file_paths]

    def apply_map(f, i):
        for x in i:
            f(x)

    assert len(file_paths) == 2
    print("Starting multiprocessing Files")

    # Serialization with Pickle requires higher recursion limit
    import sys
    previous_recursion = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)

    apply_map(multiprocessing.Process.start, ps)

    values = (parent_conn.recv(), parent_conn.recv())
    r = tuple(map(lambda x: x[1], sorted(values, key=lambda x: file_paths.index(x[0]))))

    apply_map(multiprocessing.Process.join, ps)

    print("Finished all processes")
    sys.setrecursionlimit(previous_recursion)
    return r
