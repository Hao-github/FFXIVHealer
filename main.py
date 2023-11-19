from Fight import Fight
from Jobs.Healer.Scholar import Scholar
# from .models.effect import Dot


if __name__ == "__main__":
    Fight.addPlayer("mt", 120000)
    # Fight.addPlayer("st", 120000)
    # Fight.addPlayer("h1", 80000)
    # Fight.addPlayer("h2", 80000)
    # Fight.addPlayer("d1", 80000)
    # Fight.addPlayer("d2", 80000)
    # Fight.addPlayer("d3", 80000)
    Fight.addPlayer("d4", 80000)

    sch = Scholar(80000, 25, 1.6)
    Fight.addDamageEvent(14.44, "究极", 60000)
    # Fight.addDamageEvent(20, "xiaojiuji", 30000)
    Fight.addEvent(0, sch.Succor())
    Fight.addEvent(11, sch.Recitation())
    Fight.addEvent(15, sch.Indomitability())

    Fight.run()
    Fight.showPlayerHp()
