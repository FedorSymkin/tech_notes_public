cdef extern from "examples.h":
    void hello(const char *)

def py_hello(name):
    # type: (bytes) -> None
    hello(name)
    

