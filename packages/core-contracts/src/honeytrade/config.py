from pydantic import Field
# ... existing config + new field
    POLYGON_API_KEY: Optional[str] = Field(default=None, env='POLYGON_API_KEY')
