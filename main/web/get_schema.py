# The C data structures for the web app

from cffi import FFI

FMT = {
    "uint32_t": '"%" PRIu32', "int32_t": '"%" PRId32',
    "uint16_t": '"%" PRIu16', "int8_t":   '"%" PRId8',
    "size_t":   '"%zu"',      "float":    '"%.2f"',
    "_Bool":    None,         # emitted as true/false
}

def load(path):
    ffi = FFI()
    ffi.cdef(open(path).read())
    return ffi, ffi.typeof("state_t")

def fields(ct):
    for name, f in ct.fields:
        t = f.type
        if t.kind == "primitive" and t.cname in FMT:
            yield name, t.cname, None
        elif t.kind == "array" and t.item.cname in FMT:
            yield name, t.item.cname, t.length
        else:
            raise SystemExit(f"state_t.{name}: unsupported type {t.cname}")


if __name__ == "__main__":
    path = "main/state/state_struct.h"
    ffi, ct = load(path)
    for name, cname, length in fields(ct):
        print(name, cname, length)