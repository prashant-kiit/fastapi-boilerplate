Here's the equivalent implementation in **FastAPI + SQLModel**. The client sends the **complete list of items**, and the server reconciles the database to match it.

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import Todo

router = APIRouter()


@router.post("/sync")
def sync(
    items: list[Todo],
    session: Session = Depends(get_session),
):
    # Fetch existing items
    db_items = session.exec(select(Todo)).all()

    db_map = {item.id: item for item in db_items}
    incoming_map = {item.id: item for item in items}

    # INSERT / UPDATE
    for incoming in items:
        existing = db_map.get(incoming.id)

        if existing is None:
            session.add(incoming)
        else:
            existing.title = incoming.title
            existing.status = incoming.status

    # DELETE
    for db_item in db_items:
        if db_item.id not in incoming_map:
            session.delete(db_item)

    session.commit()

    return {
        "success": True,
        "items": session.exec(select(Todo)).all(),
    }
```

### Algorithm

```text
Fetch all DB records
        │
        ▼
Create db_map (id → object)
Create incoming_map (id → object)
        │
        ▼
For each incoming item
    ├── Not in DB → INSERT
    └── Exists → UPDATE
        │
        ▼
For each DB item
    └── Missing in request → DELETE
        │
        ▼
Commit transaction
        │
        ▼
Return latest DB state
```

### Time Complexity

* Fetch DB: **O(n)**
* Build maps: **O(n)**
* Insert/Update pass: **O(n)**
* Delete pass: **O(n)**

**Overall:** **O(n)** time and **O(n)** extra space.

> This pattern is known as **state reconciliation** or **full-state synchronization**: the server makes its database state exactly match the list sent by the client.
