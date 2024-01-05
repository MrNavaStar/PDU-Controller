import subprocess


class UPS:

    def __init__(self, url):
        self.url = url

    def info(self):
        info = {}
        result = subprocess.run(["upsc", self.url], stdout=subprocess.PIPE)
        for line in result.stdout.decode("utf-8").split("\n"):
            data = line.split(": ")
            if len(data) < 2:
                continue
            info[data[0]] = data[1]
        return info

    def currentWatts(self):
        info = self.info()
        return (int(info["ups.load"]) / 100) * int(info["ups.realpower.nominal"])
