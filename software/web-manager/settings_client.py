"""Client for the local privileged settings service."""

import json
import socket


def settings_request(action, data=None):
    request = dict(data or {}, action=action)
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(45)
    try:
        client.connect("/run/makit-settings/control.sock")
        client.sendall(json.dumps(request).encode() + b"\n")
        with client.makefile("rb") as stream:
            reply = stream.readline(1048577)
        if len(reply) > 1048576:
            raise ValueError("系统设置响应过大")
        result = json.loads(reply)
        if "error" in result:
            raise ValueError(result["error"])
        return result["result"]
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("系统设置服务暂时不可用，请稍后重试") from error
    finally:
        client.close()
