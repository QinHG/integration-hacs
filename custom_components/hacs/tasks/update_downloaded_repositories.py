""""Hacs base setup task."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant

from ..base import HacsBase
from ..enums import HacsGitHubRepo, HacsStage
from .base import HacsTask


async def async_setup_task(hacs: HacsBase, hass: HomeAssistant) -> Task:
    """Set up this task."""
    return Task(hacs=hacs, hass=hass)


class Task(HacsTask):
    """Hacs update downloaded task."""

    schedule = timedelta(hours=2)
    stages = [HacsStage.STARTUP]

    async def async_execute(self) -> None:
        """Execute the task."""
        self.hacs.log.debug("Starting recurring background task for installed repositories")
        self.hacs.status.background_task = True
        self.hass.bus.async_fire("hacs/status", {})

        for repository in self.hacs.repositories.list_all:
            if self.hacs.status.startup and repository.data.full_name == HacsGitHubRepo.INTEGRATION:
                continue
            if (
                repository.data.installed
                and repository.data.category in self.hacs.common.categories
            ):
                self.hacs.queue.add(repository.update_repository())

        self.hacs.status.background_task = False
        self.hass.bus.async_fire("hacs/status", {})
        await self.hacs.data.async_write()
        self.hacs.log.debug("Recurring background task for installed repositories done")
