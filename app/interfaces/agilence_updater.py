"""Agilence integration interface scaffold."""


class AgilenceUpdater:
    def create_task(self) -> None:
        raise NotImplementedError

    def update_task(self) -> None:
        raise NotImplementedError
