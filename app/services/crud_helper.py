import math
from typing import Any, Callable, Dict, List
from flask_login import current_user
from app.extensions import crud_provider
from hogc.lib import Context
from hogc.lib.base import RequestContext as BaseRequestContext
from hogc.lib.contracts.crud.models import RecordQuery, QueryFilter, QuerySort
from hogc.lib.contracts.crud.requests import QueryRecordsRequest
from hogc.lib.contracts.crud.types import SortDirection

class EAVPagination:
    """Mock Flask-SQLAlchemy Pagination class for EAV records compatibility."""
    def __init__(self, items: List[Any], page: int, per_page: int, total: int) -> None:
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = int(math.ceil(total / per_page)) if per_page > 0 else 0

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def next_num(self) -> int:
        return self.page + 1

    @property
    def prev_num(self) -> int:
        return self.page - 1

    def iter_pages(self, left_edge: int = 2, left_current: int = 2, right_current: int = 5, right_edge: int = 2) -> Any:
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (self.page - left_current - 1 < num < self.page + right_current)
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num

def run_in_context(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run a callable within a bound HogcContext, injecting tenant, user, and execution metadata."""
    user_id = "system"
    roles = []
    if current_user and current_user.is_authenticated:
        user_id = current_user.get_id()
        roles = getattr(current_user, "role_names", [])

    token = Context.set(
        tenant_id="default",
        user_id=user_id,
        roles=roles,
        schema_name="public",
        source="http" if current_user and current_user.is_authenticated else "system"
    )
    try:
        context_dto = BaseRequestContext(
            tenant_id="default",
            org_id="default",
            user_id=user_id,
            roles=roles
        )
        return func(context_dto, *args, **kwargs)
    finally:
        Context.reset(token)

def query_records(ctx: BaseRequestContext, module_id: str, filters: Dict[str, Any], page: int = 1, page_size: int = 50, sort_field: str | None = None) -> Any:
    """Utility to query records from a module using a dictionary of equality filters."""
    query_filters = [
        QueryFilter(field=k, operator="eq", value=str(v) if v is not None else None)
        for k, v in filters.items() if v is not None
    ]
    sorts = []
    if sort_field:
        sorts.append(QuerySort(field=sort_field, direction=SortDirection.ASC))
    
    query = RecordQuery(
        module_id=module_id,
        filters=query_filters,
        sort=sorts,
        page=page,
        page_size=page_size
    )
    req = QueryRecordsRequest(context=ctx, query=query)
    return crud_provider.records.query_records(req)
