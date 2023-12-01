from Jobs.MagicDPS import Summoner
from Jobs.Tank import DarkKnight
from Fight import Fight
from Jobs.Healer import Astrologian, Scholar
from models.player import Player


if __name__ == "__main__":
    # Fight.addPlayer("mt", 120000)
    # Fight.addPlayer("st", 120000)
    # Fight.addPlayer("h1", 80000)
    # Fight.addPlayer("h2", 80000)
    # Fight.addPlayer("d1", 80000)
    # Fight.addPlayer("d2", 80000)
    # Fight.addPlayer("d3", 80000)
    # Fight.addPlayer("d4", 80000)

    sch = Scholar(hp=80000, potency=25, critNum=1.6)
    ast = Astrologian(hp=80000, potency=25)
    # dk1 = DarkKnight(hp=110000, potency=25)
    # dk2 = DarkKnight(hp=110000, potency=25)
    # smr = Summoner(hp=80000, potency=25)
    boss=Player("boss", 0, 0, 0, 0)
    Fight.addPlayer("h2", sch)
    Fight.addPlayer("h1", ast)
    Fight.addBossSkills("p9s copy.csv", boss)
    # Fight.addRecord(0.05, boss.createMagicAOE("究极", 60000))
    # Fight.addRecord(5, boss.createMagicAOE("究极", 30000))
    # Fight.addRecord(0.02, sch.Dissipation())
    # Fight.addRecord(0.1, sch.Recitation())
    # Fight.addRecord(0.2, sch.Succor())

    Fight.run()
    # Fight.showPlayerHp()
