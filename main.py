from models.boss import Boss
from Fight import Fight
from Jobs.Healer import Scholar
# from .models.effect import Dot


if __name__ == "__main__":
    # Fight.addPlayer("mt", 120000)
    # Fight.addPlayer("st", 120000)
    # Fight.addPlayer("h1", 80000)
    # Fight.addPlayer("h2", 80000)
    # Fight.addPlayer("d1", 80000)
    # Fight.addPlayer("d2", 80000)
    # Fight.addPlayer("d3", 80000)
    # Fight.addPlayer("d4", 80000)

    sch = Scholar(hp=80000, potency=25, criticalNum=1.6)
    boss = Boss("p10s")
    Fight.addPlayer(sch)
    Fight.addRecord(14.44, boss.createMagicAOE("究极", 60000))
    Fight.addRecord(20, boss.createMagicAOE("究极", 30000))
    Fight.addRecord(10, sch.Dissipation())
    Fight.addRecord(11, sch.Recitation())
    Fight.addRecord(15, sch.Succor())

    Fight.run()
    # Fight.showPlayerHp()
