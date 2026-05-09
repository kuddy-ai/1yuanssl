"""Scheduler tests."""

from app.tasks import scheduler as scheduler_module


class FakeScheduler:
    def __init__(self, running: bool = False):
        self.running = running
        self.calls: list[tuple[str, dict]] = []

    def add_job(self, *args, **kwargs) -> None:
        self.calls.append(("add_job", kwargs))

    def start(self) -> None:
        self.calls.append(("start", {}))


def test_start_scheduler_respects_disabled_setting(monkeypatch) -> None:
    fake_scheduler = FakeScheduler()

    monkeypatch.setattr(scheduler_module.settings, "SCHEDULER_ENABLED", False)
    monkeypatch.setattr(scheduler_module, "scheduler", fake_scheduler)

    scheduler_module.start_scheduler()

    assert fake_scheduler.calls == []


def test_start_scheduler_registers_renewal_job(monkeypatch) -> None:
    fake_scheduler = FakeScheduler()

    monkeypatch.setattr(scheduler_module.settings, "SCHEDULER_ENABLED", True)
    monkeypatch.setattr(scheduler_module.settings, "RENEWAL_CHECK_INTERVAL_HOURS", 12)
    monkeypatch.setattr(scheduler_module, "scheduler", fake_scheduler)

    scheduler_module.start_scheduler()

    assert fake_scheduler.calls[0][0] == "add_job"
    assert fake_scheduler.calls[0][1]["hours"] == 12
    assert fake_scheduler.calls[0][1]["id"] == "mock_certificate_renewal"
    assert fake_scheduler.calls[1][0] == "start"
