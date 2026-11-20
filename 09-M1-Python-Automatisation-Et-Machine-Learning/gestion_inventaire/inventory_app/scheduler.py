"""Planificateur quotidien léger basé uniquement sur la bibliothèque standard."""

from __future__ import annotations

from datetime import datetime, timedelta
import threading
from typing import Callable, Optional


def parse_hhmm(time_str: str) -> tuple[int, int]:
    """Valide et extrait (heure, minute) depuis une chaîne 'HH:MM'."""
    parts = time_str.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Format d'heure invalide (attendu HH:MM, ex: 08:30).")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("L'heure doit être comprise entre 00:00 et 23:59.")
    return hour, minute


def compute_next_run(time_str: str, now: Optional[datetime] = None) -> datetime:
    """Calcule le prochain horodatage d'exécution pour une heure HH:MM donnée."""
    hour, minute = parse_hhmm(time_str)
    ref = now or datetime.now()
    candidate = ref.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= ref:
        candidate += timedelta(days=1)
    return candidate


class DailyScheduler:
    """Exécute un callback chaque jour à une heure donnée dans un thread dédié."""

    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._running = False
        self.scheduled_time: Optional[str] = None
        self.next_run: Optional[datetime] = None

    @property
    def is_running(self) -> bool:
        """Indique si une planification est active."""
        with self._lock:
            return self._running

    def start(self, time_str: str) -> datetime:
        """Démarre ou reprogramme la tâche quotidienne à l'heure spécifiée."""
        parse_hhmm(time_str)
        with self._lock:
            self._cancel_timer_locked()
            self.scheduled_time = time_str.strip()
            self._running = True
            return self._arm_next_locked()

    def stop(self) -> None:
        """Arrête la planification en cours."""
        with self._lock:
            self._running = False
            self.next_run = None
            self._cancel_timer_locked()

    def _cancel_timer_locked(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _arm_next_locked(self) -> datetime:
        assert self.scheduled_time is not None
        target = compute_next_run(self.scheduled_time)
        self.next_run = target
        delay = max(0.5, (target - datetime.now()).total_seconds())
        self._timer = threading.Timer(delay, self._run_and_reschedule)
        self._timer.daemon = True
        self._timer.start()
        return target

    def _run_and_reschedule(self) -> None:
        try:
            self._callback()
        finally:
            with self._lock:
                if self._running and self.scheduled_time is not None:
                    self._arm_next_locked()
