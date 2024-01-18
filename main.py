import os
from Fight import Fight


if __name__ == "__main__":
    try:
        Fight.addbaseCofig("P9S.xlsx")
        Fight.run(0.01)
        print("结果已输出至output.csv")
    except Exception as e:
        print(e)
        print("报错惹, 把报错的原因和结果都截个图记录一下一起发给我")
    finally:
        os.system("pause")
