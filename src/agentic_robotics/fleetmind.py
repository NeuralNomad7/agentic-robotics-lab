"""Capability-aware task allocation with leases and failure recovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot


@dataclass
class Robot:
    robot_id: str
    capabilities: frozenset[str]
    position: tuple[float, float]
    battery: float
    active_tasks: int = 0
    last_heartbeat: float = 0.0


@dataclass(frozen=True)
class Task:
    task_id: str
    capability: str
    position: tuple[float, float]
    priority: float = 1.0


@dataclass(frozen=True)
class Lease:
    task_id: str
    robot_id: str
    expires_at: float
    bid: float


@dataclass
class FleetCoordinator:
    lease_seconds: float = 30.0
    heartbeat_timeout: float = 15.0
    robots: dict[str, Robot] = field(default_factory=dict)
    leases: dict[str, Lease] = field(default_factory=dict)

    def register(self, robot: Robot) -> None:
        self.robots[robot.robot_id] = robot

    def heartbeat(
        self,
        robot_id: str,
        now: float,
        *,
        position: tuple[float, float] | None = None,
        battery: float | None = None,
    ) -> None:
        robot = self.robots[robot_id]
        robot.last_heartbeat = now
        if position is not None:
            robot.position = position
        if battery is not None:
            robot.battery = battery

    def allocate(self, task: Task, now: float) -> Lease | None:
        current = self.leases.get(task.task_id)
        if current and current.expires_at > now and self._healthy(current.robot_id, now):
            return current

        candidates = [
            robot
            for robot in self.robots.values()
            if task.capability in robot.capabilities and self._healthy(robot.robot_id, now)
        ]
        if not candidates:
            self.release(task.task_id)
            return None

        winner = max(candidates, key=lambda robot: self._bid(robot, task))
        if current:
            self._unload(current.robot_id)
        winner.active_tasks += 1
        lease = Lease(
            task_id=task.task_id,
            robot_id=winner.robot_id,
            expires_at=now + self.lease_seconds,
            bid=self._bid(winner, task),
        )
        self.leases[task.task_id] = lease
        return lease

    def release(self, task_id: str) -> None:
        lease = self.leases.pop(task_id, None)
        if lease:
            self._unload(lease.robot_id)

    def _unload(self, robot_id: str) -> None:
        robot = self.robots.get(robot_id)
        if robot and robot.active_tasks > 0:
            robot.active_tasks -= 1

    def _healthy(self, robot_id: str, now: float) -> bool:
        robot = self.robots.get(robot_id)
        if robot is None:
            return False
        return robot.battery >= 0.15 and now - robot.last_heartbeat <= self.heartbeat_timeout

    @staticmethod
    def _bid(robot: Robot, task: Task) -> float:
        distance = hypot(robot.position[0] - task.position[0], robot.position[1] - task.position[1])
        return task.priority * 10.0 + robot.battery * 5.0 - distance - robot.active_tasks * 2.0
