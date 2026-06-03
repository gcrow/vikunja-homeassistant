from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyvikunja.models.task import Task

from custom_components.vikunja import DOMAIN, LOGGER
from custom_components.vikunja.const import DATA_BUCKETS_KEY, DATA_TASKS_KEY


class VikunjaTaskEntity(CoordinatorEntity):
    """Base class for all Vikunja Task entities."""

    def __init__(self, coordinator, base_url, task_id):
        """Initialize the entity."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._task_id = task_id
        self._base_url = base_url

    @property
    def task(self) -> Task:
        return self._coordinator.data[DATA_TASKS_KEY][self._task_id]

    def project_bucket_data(self) -> dict | None:
        """Kanban bucket cache for this task's project, if the project has a kanban view."""
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get(DATA_BUCKETS_KEY, {}).get(self.task.project_id)

    def name_prefix(self):
        return f"{self.task.title}"

    def id_prefix(self):
        return f"task_{self.task.id}"

    @property
    def device_info(self):
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.id_prefix())},
            name=self.name_prefix(),
            manufacturer="Vikunja",
            model="Task",
            configuration_url=self._base_url + f"/tasks/{self.task.id}"
        )

    async def async_update(self):
        """Request an update from the coordinator."""
        await self._coordinator.async_request_refresh()

    async def update_task(self):
        await self.async_update()
        """Update the coordinator's stored task data and trigger an update."""
        self._coordinator.async_update_listeners()
