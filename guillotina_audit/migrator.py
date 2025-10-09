from elasticsearch import NotFoundError
from elasticsearch import TransportError
from guillotina.component import get_utility
from guillotina_audit.interfaces import IAuditUtility

import asyncio
import datetime
import logging


logger = logging.getLogger("guillotina_audit")
logger.setLevel(logging.INFO)


class Migrator:
    description = (
        "Migrate index to a new index maintaining the name of the index as an alias"
    )

    def __init__(self):
        self.util = get_utility(IAuditUtility)
        self.es = self.util.async_es
        self.alias = self.util.index

    def _new_index_name(self) -> str:
        # e.g., audit-20251009-121314
        ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return f"{self.alias}-{ts}"

    async def _get_index_pointed_by_alias(self):
        try:
            data = await self.es.indices.get_alias(name=self.alias)
            # Usually a single index; pick the first key deterministically
            current_index = sorted(data.keys())[0]
            return current_index
        except NotFoundError:
            return None

    async def _ensure_alias_exists_if_raw_index(self):
        """
        If there is no alias yet but there *is* a raw index with the alias name
        (e.g., an index literally named 'audit'), create the alias on it so we
        can perform an atomic swap later.
        Returns the current concrete index name if it exists, else None.
        """
        exists = await self.es.indices.exists(index=self.alias)
        if exists:
            return self.alias
        return None

    async def _create_new_index(self, new_index: str):
        dm = self.util.default_mappings()
        try:
            await self.es.indices.create(
                index=new_index,
                settings=self.util.default_settings(),
                mappings=dm,
            )
            logger.info("Created index %s", new_index)
        except TransportError:
            logger.error("Failed creating %s", new_index, exc_info=True)
            raise

    async def _reindex(self, src: str, dest: str, wait: bool = True):
        body = {"source": {"index": src}, "dest": {"index": dest, "op_type": "create"}}
        try:
            data = await self.es.reindex(
                body=body,
                wait_for_completion=False,
                refresh=True,
                slices="auto",
                request_timeout=60 * 60 * 3,  # up to 3 hour for big datasets
            )
            logger.info("Reindex response: %s", data)
            task_completed = False
            task_id = data["task"]
            while not task_completed:
                await asyncio.sleep(10)
                data = await self.es.tasks.get(task_id=task_id)
                status = data["task"]["status"]
                logger.info(
                    f'{status["created"]}/{status["total"]} - '
                    f"Copying data to new index. task id: {task_id}"
                )
                task_completed = data["completed"]
                if task_completed:
                    break
        except TransportError:
            logger.error("Reindex from %s to %s failed", src, dest, exc_info=True)
            raise

    async def _swap_alias(self, old_index: str, new_index: str):
        actions = []
        # Mark new index as the write index for this alias (handy for future rollovers)
        actions.append(
            {"add": {"index": new_index, "alias": self.alias, "is_write_index": True}}
        )

        await self.es.indices.update_aliases(body={"actions": actions})
        logger.info("Alias %s now points to %s", self.alias, new_index)

    async def migrate(self, delete_old: bool = False):
        """
        Perform migration:
          - find current concrete index behind alias (or raw index)
          - create a new index with default settings/mappings
          - reindex data
          - atomically swap alias
          - optionally delete old index
        Returns: the new index name.
        """
        # Make sure we don't auto-create unexpected indices
        try:
            await self.es.cluster.put_settings(
                body={"persistent": {"action.auto_create_index": "false"}}
            )
        except TransportError:
            logger.warning(
                "Could not set cluster auto_create_index=false", exc_info=True
            )
        current_index = await self._get_index_pointed_by_alias()
        if current_index is None:
            # Maybe there is a raw index literally named the same as the alias
            current_index = await self._ensure_alias_exists_if_raw_index()
        if current_index is None:
            current_index = self.util.index
        new_index = self._new_index_name()
        await self._create_new_index(new_index)
        # Only reindex if there is a source
        if current_index:
            try:
                await self._reindex(src=current_index, dest=new_index, wait=True)
                await self.es.indices.put_settings(
                    index=current_index, body={"index": {"blocks.write": True}}
                )
                await self.es.indices.delete(index=current_index)
                await self._swap_alias(old_index=current_index, new_index=new_index)
            except NotFoundError:
                pass
            except TransportError:
                logger.warning(
                    "Failed deleting old index %s", current_index, exc_info=True
                )
        else:
            logger.info(
                "No existing index behind alias '%s'. Fresh index created: %s",
                self.alias,
                new_index,
            )
        return new_index
