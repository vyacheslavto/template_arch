from typing import Annotated

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column

dt_utcnow = Annotated[
    TIMESTAMP,
    mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("timezone('utc', now())"),
    ),
]

dt_with_tz = Annotated[
    TIMESTAMP, mapped_column(TIMESTAMP(timezone=True), nullable=False)
]
