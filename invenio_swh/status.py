# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-SWH is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""SHW deposit status classes."""

from invenio_swh.errors import StatusMismatch
from invenio_swh.utils import classproperty


class DepositStatus:  # State API

    _context = None

    @classproperty
    def value(cls):
        raise NotImplementedError

    def update(self, new_status):
        # if self._context != known_status:
        # raise ValueError("Can't update status of deposit.")
        self.handler.set(new_status)


class Pending(DepositStatus):
    @classproperty
    def value(cls):
        return "P"

    def __init__(self, context):
        self._context = context

    def update(self, new_status):
        pass


class Completed(DepositStatus):
    @classproperty
    def value(cls):
        return "C"

    def __init__(self, context):
        self._context = context


class Failed(DepositStatus):

    @classproperty
    def value(cls):
        return "F"

    def __init__(self, context):
        self._context = context


class Waiting(DepositStatus):
    @classproperty
    def value(cls):
        return "W"

    def __init__(self, context):
        self._context = context


class StatusHandler:  # like a systemfield

    def __init__(self, deposit):
        self._deposit = deposit

    def _check_concurrency(self, deposit, expected_status: DepositStatus):
        _val = getattr(expected_status, "value")
        if _val is not None and deposit.status != _val:
            raise StatusMismatchError(deposit.status, expected_status)

    def set(self, status: DepositStatus, expected_status: DepositStatus):
        current_status = self._deposit.status
        self._deposit.model.status = getattr(status, "value")


# deposit.status.update()
# deposit.status.set(Pending(), deposit.status)
