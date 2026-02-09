import os
from mcp.server.fastmcp import FastMCP
from typing import Optional, List
import requests
from uuid import UUID


AI_BACKEND_URL = os.getenv("AI_BACKEND_URL", "http://localhost:8000")

mcp = FastMCP("mcp-server")

@mcp.tool(
    description="""
This tool generates a laboratory test CRF form.

STRICT SCHEMA RULES (MUST FOLLOW):
- All fields must strictly follow the provided schema.
- The `type` field of each laboratory test item MUST be one of the following values ONLY:
  - "textarea"
  - "number"
  - "date"
  - "time"
  - "dateTime"
  - "radio"
  - "checkbox"
  - "single-select"
  - "multiple-select"
  - "text"
  - "file"

DO NOT invent new types.
DO NOT use synonyms such as "string", "int", "select", "dropdown", or "boolean".

LABORATORY TEST ITEM RULES:
Each item MUST include:
- label: a human-readable name.
- code: a machine-readable identifier (no spaces).
- type: one of the allowed input types.
- options:
  - REQUIRED and MUST be NON-EMPTY when type is one of:
    "radio", "checkbox", "single-select", "multiple-select".
  - MUST be an empty list [] for all other types.

DO NOT include options for types that do not support options.

ATTACHMENT RULE:
- `attachment_uid` is required and identifies the file or CRF context used to generate the laboratory test form.

If any field violates these rules, DO NOT call the tool.
Revise the output until it fully complies with the schema.

EXAMPLE VALID INPUT:
{
  "items": [
    {
      "label": "Blood Type",
      "code": "BLOOD_TYPE",
      "type": "single-select",
      "unit": null,
      "options": [
        {"label": "A", "value": "A"},
        {"label": "B", "value": "B"},
        {"label": "AB", "value": "AB"},
        {"label": "O", "value": "O"}
      ]
    }
  ],
  "user_prompt": [
    "Generate a laboratory test CRF form based on the provided items."
  ]
}
"""
)
async def laboratory_test(
    attachment_uid: UUID,
    items: Optional[List] = None,
    user_prompt: Optional[List[str]] = None,
) -> dict:
    payload = {
        "items": items or [],
        "user_prompt": user_prompt,
    }

    response = requests.post(
        f"{AI_BACKEND_URL}/api/crfs/laboratory-test/{attachment_uid}",
        json=payload,
        timeout=60,
    )

    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    mcp.run()
