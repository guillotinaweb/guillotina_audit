from guillotina import task_vars
from guillotina.tests import utils
from guillotina.tests.utils import get_container


async def setup_txn_on_container(requester, container_id="guillotina"):
    utils.login()
    request = utils.get_mocked_request(db=requester.db)
    task_vars.request.set(request)
    container = await get_container(
        requester=requester, container_id=container_id
    )  # noqa
    tm = task_vars.tm.get()
    txn = await tm.begin()
    return container, request, txn, tm
