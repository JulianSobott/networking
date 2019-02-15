"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net


def dummy_func(name):
    print(f"Hello {name}")
    return f"Goodbye {name}"


if __name__ == '__main__':
    server = net.Server("127.0.0.1", "5000")

