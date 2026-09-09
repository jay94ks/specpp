"""examples/doom/intermission.md 의 # Domain/# Behavior 참조 구현."""


class Intermission:
    def __init__(self, finishedMapName, nextMapName, killPercent, itemPercent,
                 secretPercent, parTimeTics, playerTimeTics):
        self.finishedMapName = finishedMapName
        self.nextMapName = nextMapName
        self.killPercent = killPercent
        self.itemPercent = itemPercent
        self.secretPercent = secretPercent
        self.parTimeTics = parTimeTics
        self.playerTimeTics = playerTimeTics


class Finale:
    def __init__(self, text, castOfCharacters=None):
        self.text = text
        self.castOfCharacters = castOfCharacters


def _percent(count, total):
    if total <= 0:
        return 100
    return int(round(100 * count / total))


# spp-source: examples/doom/intermission.md#Feature:_스테이지_클리어_전환
def make_intermission(finishedMapName, nextMapName, killCount, totalKills,
                       itemCount, totalItems, secretCount, totalSecrets,
                       parTimeTics, playerTimeTics):
    return Intermission(
        finishedMapName=finishedMapName,
        nextMapName=nextMapName,
        killPercent=_percent(killCount, totalKills),
        itemPercent=_percent(itemCount, totalItems),
        secretPercent=_percent(secretCount, totalSecrets),
        parTimeTics=parTimeTics,
        playerTimeTics=playerTimeTics,
    )
