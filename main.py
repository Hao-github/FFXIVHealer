from Fight import Fight
from Scholar import Scholar


if __name__ == "__main__":
    Fight.addPlayer("mt", 120000)
    # Fight.addPlayer("st", 120000)
    # Fight.addPlayer("h1", 80000)
    # Fight.addPlayer("h2", 80000)
    # Fight.addPlayer("d1", 80000)
    # Fight.addPlayer("d2", 80000)
    # Fight.addPlayer("d3", 80000)
    Fight.addPlayer("d4", 80000)

    sch = Scholar(25, 1.6)
    Fight.addDamageEvent(10, 60000)
    Fight.addDamageEvent(20, 30000)
    Fight.addEvent(0, sch.Succor())
    Fight.addEvent(11, sch.Recitation())
    Fight.addEvent(15, sch.Indomitability())

    Fight.run()
    Fight.showPlayerHp()
