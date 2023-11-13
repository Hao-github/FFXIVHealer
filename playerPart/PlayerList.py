from playerPart.effect import Hot, Dot
from playerPart.player import Player
class PlayerList:
    ## 以仇恨值排序
    playerList: list[Player] = []

    @classmethod
    def addPlayer(cls, player: Player) -> None:
        cls.playerList.append(player)
        player.getEffect(Hot("naturalHeal", float("inf"), player.maxHp // 100))

    @classmethod
    def getAOEHurt(cls, damage: int, dot: Dot | None = None) -> None:
        for player in cls.playerList:
            PlayerList.getAAAttack(player, damage, dot)

    @classmethod
    def getAAAttack(cls, player: Player, damage: int, dot: Dot | None = None) -> None:
        player.getDamage(damage)
        if dot:
            player.getEffect(dot)

