"""Native window constraints missing from Pyxel's public API."""

import ctypes
import sys


class Size(ctypes.Structure):
    _fields_ = [('width', ctypes.c_double), ('height', ctypes.c_double)]


def lock_window_size(width: int, height: int) -> None:
    if sys.platform != 'darwin':
        return

    runtime = ctypes.CDLL('/usr/lib/libobjc.A.dylib')
    runtime.objc_getClass.argtypes = [ctypes.c_char_p]
    runtime.objc_getClass.restype = ctypes.c_void_p
    runtime.sel_registerName.argtypes = [ctypes.c_char_p]
    runtime.sel_registerName.restype = ctypes.c_void_p

    def send(receiver, selector, result, args=(), values=()):
        signature = ctypes.CFUNCTYPE(result, ctypes.c_void_p, ctypes.c_void_p, *args)
        method = signature(('objc_msgSend', runtime))
        return method(receiver, runtime.sel_registerName(selector), *values)

    pointer = ctypes.c_void_p
    application = send(runtime.objc_getClass(b'NSApplication'), b'sharedApplication', pointer)
    windows = send(application, b'windows', pointer)
    count = send(windows, b'count', ctypes.c_ulong)
    for index in range(count):
        window = send(windows, b'objectAtIndex:', pointer, (ctypes.c_ulong,), (index,))
        mask = send(window, b'styleMask', ctypes.c_ulong)
        send(window, b'setStyleMask:', None, (ctypes.c_ulong,), (mask & ~(1 << 3),))
        for selector in (b'setContentMinSize:', b'setContentMaxSize:', b'setContentSize:'):
            send(window, selector, None, (Size,), (Size(width, height),))
        zoom = send(window, b'standardWindowButton:', pointer, (ctypes.c_ulong,), (2,))
        send(zoom, b'setEnabled:', None, (ctypes.c_bool,), (False,))
