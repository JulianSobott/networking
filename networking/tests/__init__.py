"""
@author: Julian Sobott
@created: XX.XX.2019
@brief:
@description:

@external_use:

@internal_use:

@TODO:
"""
from networking.utils import time_func

@time_func
def main():
    with open("dummy.txt", "r") as f:
        i = 0
        file_data = f.read(1024)
        while len(file_data) > 0:
            i += len(file_data)
            file_data = f.read(1024)
        print(i)


if __name__ == '__main__':
    main()