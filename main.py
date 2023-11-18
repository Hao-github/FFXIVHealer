from Fight import Fight


if __name__ == "__main__":
    Fight.addPlayer("mt", 120000)
    Fight.addPlayer("st", 120000)
    Fight.addPlayer("h1", 80000)
    Fight.addPlayer("h2", 80000)
    Fight.addPlayer("d1", 80000)
    Fight.addPlayer("d2", 80000)
    Fight.addPlayer("d3", 80000)
    Fight.addPlayer("d4", 80000)

    Fight.addDamageEvent(10, 60000)
    Fight.addDamageEvent(20, 60000)
    Fight.addShieldEvent(0, 20000)
    Fight.addHealEvent(15, 30000)

    Fight.run()
    pass
