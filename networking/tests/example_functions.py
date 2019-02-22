"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net
from Logging import logger


class DummyPerson:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        if isinstance(other, DummyPerson):
            return (self.name == other.name
                    and self.age == other.age)


def no_arg_no_ret() -> None:
    print("no_arg_no_ret() called")


def no_arg_ret() -> bool:
    print("no_arg_ret() called")
    return True


def immutable_args_ret(name: str, age: int, children: tuple) -> str:
    return f"{name} is {age} old and has {len(children)}: {children}"


def args_ret_object(name, age) -> DummyPerson:
    return DummyPerson(name, age)


def class_args_ret(person: DummyPerson) -> tuple:
    name = person.name
    age = person.age
    return name, age


def huge_args_huge_ret(*args):
    return args
