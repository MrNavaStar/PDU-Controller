import subprocess


class UPS:

    def __init__(self, url):
        self.url = url

    def info(self):
        info = {}
        result = subprocess.run(['upsc', self.url], stdout=subprocess.PIPE)
        for line in result.stdout.decode('utf-8').replace("Init SSL without certificate database", "").split("\n"):
            data = line.split(": ")
            if len(data) < 2:
                continue
            info[data[0]] = data[1]
        return info


if __name__ == '__main__':
    ups = UPS("cyberpower@localhost")
    print(ups.info())
