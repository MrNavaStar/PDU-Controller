import subprocess


class UPS:

    def __init__(self, url):
        self.url = url

    def info(self):
        info = {}
        result = subprocess.run(['upsc', self.url], stdout=subprocess.PIPE)
        for line in result.stdout.decode('utf-8').replace("Init SSL without certificate database", "").split("\n"):
            data = line.split(": ")
            info[data[0]] = data[1]
