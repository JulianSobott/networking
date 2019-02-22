"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import networking as net
from Logging import logger


def no_arg_ret() -> bool:
    logger.debug("c_no_arg_ret() called")
    return True


def immutable_args_ret(name: str, age: int, children: tuple) -> str:
    return f"{name} is {age} old and has {len(children)}: {children}"

