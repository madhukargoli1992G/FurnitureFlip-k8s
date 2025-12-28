from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict


app = FastAPI(title="FurnitureFlip Backend", version="1.0")

# Allow local + service-to-service calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Models
# -----------------------------
class AgentInterpretRequest(BaseModel):
    message: str
    state: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class AgentInterpretResponse(BaseModel):
    reply: str
    patch: Dict[str, Any] = Field(default_factory=dict)


class FormRequest(BaseModel):
    category: str


class FormField(BaseModel):
    key: str
    label: str
    type: str = "text"  # text/select/number/money/textarea
    required: bool = False
    default: Any = ""
    options: Optional[List[str]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None


class FormResponse(BaseModel):
    title: str
    fields: List[FormField]


class ItemIn(BaseModel):
    """
    This is intentionally forgiving:
    - accepts extra fields
    - provides safe defaults so frontend won't 422
    """
    category: str = "chair"
    name: str = ""
    condition: str = "good"
    buy_price: float = 0.0
    repair_cost: float = 0.0
    fees_pct: float = 0.0
    notes: str = ""
    material: str = "wood"
    seats: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class ItemOut(ItemIn):
    id: int


# -----------------------------
# In-memory "DB"
# -----------------------------
ITEMS: List[ItemOut] = []
NEXT_ID = 1


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health():
    return {"ok": True}


@app.post("/agent/interpret", response_model=AgentInterpretResponse)
def agent_interpret(req: AgentInterpretRequest):
    msg = (req.message or "").lower()

    # detect category from message
    category = None
    for c in ["chair", "table", "sofa", "desk", "bed", "dresser"]:
        if c in msg:
            category = c
            break

    if category:
        patch = dict(req.state or {})
        patch["category"] = category
        return AgentInterpretResponse(
            reply=f"Got it — you're selling a **{category}**. I'll generate the form now.",
            patch=patch,
        )

    return AgentInterpretResponse(
        reply="What type of furniture are you selling? (chair / table / sofa / desk / bed / dresser)",
        patch=req.state or {},
    )


@app.post("/form", response_model=FormResponse)
def get_form(req: FormRequest):
    cat = (req.category or "chair").lower().strip()

    # Basic common fields
    fields: List[FormField] = [
        FormField(key="name", label="Item name", type="text", required=True, default=""),
        FormField(
            key="condition",
            label="Condition",
            type="select",
            required=True,
            default="good",
            options=["new", "good", "fair", "poor"],
        ),
        FormField(key="buy_price", label="Purchase price ($)", type="money", required=True, default=0.0, min=0.0, step=1.0),
        FormField(key="repair_cost", label="Repair cost ($)", type="money", required=True, default=0.0, min=0.0, step=1.0),
        FormField(key="fees_pct", label="Platform fees (%)", type="number", required=True, default=0.0, min=0.0, max=100.0, step=1.0),
        FormField(key="notes", label="Notes (optional)", type="textarea", required=False, default=""),
        FormField(
            key="material",
            label="Material (optional)",
            type="select",
            required=False,
            default="wood",
            options=["wood", "metal", "plastic", "leather", "fabric", "glass", "mixed"],
        ),
    ]

    # category-specific
    if cat in ("chair", "sofa", "bed"):
        fields.append(FormField(key="seats", label="Seats (optional)", type="number", required=False, default=1, min=1, step=1))

    return FormResponse(title=f"FurnitureFlip — {cat.title()} Form", fields=fields)


@app.post("/items", response_model=ItemOut)
def create_item(item: ItemIn):
    global NEXT_ID

    try:
        data = item.model_dump()
    except Exception:
        # fallback for older pydantic
        data = dict(item)

    # Hard safety defaults
    data["fees_pct"] = float(data.get("fees_pct") or 0.0)
    data["buy_price"] = float(data.get("buy_price") or 0.0)
    data["repair_cost"] = float(data.get("repair_cost") or 0.0)
    data["name"] = str(data.get("name") or "")
    data["condition"] = str(data.get("condition") or "good")
    data["material"] = str(data.get("material") or "wood")
    data["notes"] = str(data.get("notes") or "")
    data["category"] = str(data.get("category") or "chair")

    # Seats: normalize int or None
    seats = data.get("seats")
    if seats is None:
        data["seats"] = None
    else:
        try:
            data["seats"] = int(float(seats))
        except Exception:
            data["seats"] = None

    # Clamp values
    data["fees_pct"] = max(0.0, min(100.0, data["fees_pct"]))
    data["buy_price"] = max(0.0, data["buy_price"])
    data["repair_cost"] = max(0.0, data["repair_cost"])

    item_out = ItemOut(**data, id=NEXT_ID)
    NEXT_ID += 1
    ITEMS.append(item_out)
    return item_out



@app.get("/items", response_model=List[ItemOut])
def list_items():
    return ITEMS


@app.post("/comps")
def comps(payload: Dict[str, Any]):
    """
    Stub comps endpoint: returns demo comps.
    Replace later with real Google/Serp/Marketplace scraping.
    """
    category = (payload.get("category") or "chair").lower()
    name = payload.get("name") or ""

    demo = [
        {"title": f"{name} {category} - listing A", "price": "$45", "source": "demo", "link": "https://example.com/a"},
        {"title": f"{name} {category} - listing B", "price": "$60", "source": "demo", "link": "https://example.com/b"},
        {"title": f"{name} {category} - listing C", "price": "$75", "source": "demo", "link": "https://example.com/c"},
        {"title": f"{name} {category} - listing D", "price": "$90", "source": "demo", "link": "https://example.com/d"},
    ]
    return {"items": demo}
