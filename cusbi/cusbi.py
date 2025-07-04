import serial


class CUsbI:
    def __init__(self, path: str, password: str = "pass"):
        self.path = path
        # password is padded with spaces to exactly 8 byte
        self.password = "{:<8}".format(password)

    def __enter__(self):
        self.s = serial.Serial(self.path, timeout=1)
        resp = self._send_cmd("?Q")
        # This script was only tested with this version. If you find a different version
        # in the field, lmk.
        assert resp == "CENTOS000104v04", f"Unknown firmware version: {resp}"
        return self

    def __exit__(self, type, value, traceback):
        self.s.close()

    def _deserialize_port_states(self, text: str) -> int:
        assert len(text) == 8
        text = (
            text[6]
            + text[7]
            + text[4]
            + text[5]
            + text[2]
            + text[3]
            + text[0]
            + text[1]
        )
        return int(text, 16)

    def _serialize_port_states(self, value: int) -> str:
        assert value >= 0 and value < (1 << 32)
        text = "{:08X}".format(value)
        text = (
            text[6]
            + text[7]
            + text[4]
            + text[5]
            + text[2]
            + text[3]
            + text[0]
            + text[1]
        )
        return text

    def _get_port_states(self) -> int:
        resp = self._send_cmd("GP")
        return self._deserialize_port_states(resp)

    def _set_port_states(self, states: int) -> int:
        query = self._serialize_port_states(states)
        resp = self._send_cmd("SP" + self.password + query)
        assert resp[0] == "G"
        return self._deserialize_port_states(resp[1:])

    def _send_cmd(self, cmd: str) -> str:
        # clear read buffer
        self.s.read_all()

        self.s.write(bytes(cmd, encoding="ascii") + b"\r")

        line = self.s.read_until()

        resp = str(line, encoding="ascii")
        assert resp.endswith("\r\n")

        resp = resp.strip("\n").strip("\r")
        assert "\r" not in resp and "\n" not in resp

        return resp

    # Example - switch port 3 off:
    # Sent:      'GP'        'SPpass    FBFFFFFF'
    # Recevide:     'FFFFFFFF'                  'GFBFFFFFF'
    def port_power_on(self, port: int, on: bool):
        current_states = self._get_port_states()

        if on:
            requested_states = current_states | (1 << (port - 1))
        else:
            requested_states = current_states & ~(1 << (port - 1))

        if requested_states == current_states:
            # nothing to do
            return

        current_states = self._set_port_states(requested_states)
        assert current_states == requested_states
