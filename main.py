from Fight import Fight


if __name__ == "__main__":
    Fight.addbaseCofig("Settings/p9s.csv", "Settings/p9sjob.csv", "Settings/p9shealing.csv")
    Fight.run(0.01)
