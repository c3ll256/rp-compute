"""Authenticate the service user's existing Linux password through PAM."""

import ctypes
import ctypes.util


class Message(ctypes.Structure):
    _fields_ = [("style", ctypes.c_int), ("text", ctypes.c_char_p)]


class Response(ctypes.Structure):
    _fields_ = [("text", ctypes.c_void_p), ("code", ctypes.c_int)]


Conversation = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(Message)),
    ctypes.POINTER(ctypes.POINTER(Response)), ctypes.c_void_p)


class ConversationData(ctypes.Structure):
    _fields_ = [("callback", Conversation), ("data", ctypes.c_void_p)]


def authenticate(username, password):
    pam = ctypes.CDLL(ctypes.util.find_library("pam"))
    libc = ctypes.CDLL(ctypes.util.find_library("c"))
    libc.calloc.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
    libc.calloc.restype = ctypes.c_void_p
    libc.strdup.argtypes = [ctypes.c_char_p]
    libc.strdup.restype = ctypes.c_void_p
    libc.free.argtypes = [ctypes.c_void_p]
    credentials = {1: password.encode(), 2: username.encode()}

    @Conversation
    def converse(count, messages, responses, _):
        if not 0 < count <= 32:
            return 19  # PAM_CONV_ERR
        pointer = libc.calloc(count, ctypes.sizeof(Response))
        if not pointer:
            return 5  # PAM_BUF_ERR
        result = ctypes.cast(pointer, ctypes.POINTER(Response))
        for index in range(count):
            style = messages[index].contents.style
            if style in credentials:
                result[index].text = libc.strdup(credentials[style])
                if result[index].text:
                    continue
            elif style in (3, 4):  # PAM_ERROR_MSG / PAM_TEXT_INFO
                continue
            for previous in range(index + 1):
                libc.free(result[previous].text)
            libc.free(pointer)
            return 19
        responses[0] = result  # PAM owns the response allocations after success.
        return 0

    pam.pam_start.argtypes = [ctypes.c_char_p, ctypes.c_char_p,
                              ctypes.POINTER(ConversationData), ctypes.POINTER(ctypes.c_void_p)]
    pam.pam_authenticate.argtypes = [ctypes.c_void_p, ctypes.c_int]
    pam.pam_acct_mgmt.argtypes = [ctypes.c_void_p, ctypes.c_int]
    pam.pam_end.argtypes = [ctypes.c_void_p, ctypes.c_int]
    handle = ctypes.c_void_p()
    conversation = ConversationData(converse, None)
    status = pam.pam_start(b"login", username.encode(), ctypes.byref(conversation), ctypes.byref(handle))
    if status:
        return False
    try:
        status = pam.pam_authenticate(handle, 0)
        if status == 0:
            status = pam.pam_acct_mgmt(handle, 0)
        return status == 0
    finally:
        pam.pam_end(handle, status)
