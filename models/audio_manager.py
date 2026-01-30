import subprocess


def sh(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()


class AudioManager:
    def __init__(self):
        self.modules = []
        self.sink_name = "rec_sink"

    def get_system_source(self):
        return sh("pactl get-default-sink") + ".monitor"

    def get_mic_source(self):
        return sh("pactl get-default-source")

    def load(self, args: str):
        mid = sh(f"pactl load-module {args}")
        self.modules.append(mid)

    def setup_mix(self):
        self.load(f"module-null-sink sink_name={self.sink_name}")

        self.load(
            f"module-loopback "
            f"source={self.get_mic_source()} "
            f"sink={self.sink_name}"
        )

        self.load(
            f"module-loopback "
            f"source={self.get_system_source()} "
            f"sink={self.sink_name}"
        )

    def cleanup(self):
        for mid in self.modules:
            subprocess.call(["pactl", "unload-module", mid])
        self.modules.clear()


    def prepare(self, mode):
        if mode.name == "SYSTEM":
            return self.get_system_source()

        if mode.name == "MIC":
            return self.get_mic_source()

        if mode.name == "BOTH":
            self.setup_mix()
            return f"{self.sink_name}.monitor"

        return None


