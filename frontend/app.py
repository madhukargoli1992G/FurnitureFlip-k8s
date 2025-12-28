import os
import re
import requests
import pandas as pd
import streamlit as st

API = os.getenv("API_BASE", "http://backend:8000").rstrip("/")

st.set_page_config(page_title="FurnitureFlip", layout="centered")
st.title("🪑 FurnitureFlip")
st.caption("Chat → agent detects item → dynamic form → submit → comps + recommendation dashboard")


# ---------------- Helpers ----------------
def post_json(path: str, payload: dict, timeout: int = 30):
    url = f"{API}{path}"
    r = requests.post(url, json=payload, timeout=timeout)
    return r

def parse_price(x):
    if x is None:
        return None
    s = str(x).replace(",", "")
    m = re.search(r"(\d+(?:\.\d{1,2})?)", s)
    if not m:
        return None
    try:
        return float(m.group(1))
    except:
        return None


# ---------------- Session ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {}
if "schema" not in st.session_state:
    st.session_state.schema = None
if "last_item" not in st.session_state:
    st.session_state.last_item = None
if "last_comps" not in st.session_state:
    st.session_state.last_comps = None


# ---------------- Chat ----------------
st.subheader("💬 Chat")

with st.form("chat_form", clear_on_submit=True):
    user_msg = st.text_input("Say what you want to sell (e.g., “I want to sell a chair”)…")
    c1, c2 = st.columns([1, 1])
    send = c1.form_submit_button("Send")
    clear = c2.form_submit_button("Clear chat")

if clear:
    st.session_state.chat = []
    st.session_state.agent_state = {}
    st.session_state.schema = None
    st.session_state.last_item = None
    st.session_state.last_comps = None
    st.rerun()

if send and user_msg.strip():
    st.session_state.chat.append(("You", user_msg.strip()))

    try:
        r = post_json("/agent/interpret", {"message": user_msg.strip(), "state": st.session_state.agent_state})
        if r.status_code != 200:
            st.session_state.chat.append(("Agent", f"Backend error: {r.status_code}"))
        else:
            data = r.json()
            reply = data.get("reply", "")
            patch = data.get("patch", {}) or {}
            st.session_state.agent_state.update(patch)
            st.session_state.chat.append(("Agent", reply))

            # If we now have category, fetch form schema
            cat = st.session_state.agent_state.get("category")
            if cat:
                r2 = post_json("/form", {"category": cat})
                if r2.status_code == 200:
                    st.session_state.schema = r2.json()

    except Exception as e:
        st.session_state.chat.append(("Agent", f"Error: {e}"))

for who, msg in st.session_state.chat[-10:]:
    st.markdown(f"**{who}:** {msg}")

st.divider()


# ---------------- Dynamic Form ----------------
schema = st.session_state.schema
category = st.session_state.agent_state.get("category")

if schema and category:
    st.subheader(f"🧾 {schema.get('title','FurnitureFlip Form')}")

    fields = schema.get("fields", [])
    form_data = {}

    with st.form("item_form"):
        for f in fields:
            key = f.get("key")
            label = f.get("label", key)
            ftype = f.get("type", "text")
            required = bool(f.get("required", False))

            default = f.get("default", "")

            if ftype == "select":
                opts = f.get("options") or []
                if not opts:
                    opts = [str(default)] if default else [""]
                index = opts.index(default) if default in opts else 0
                form_data[key] = st.selectbox(label + (" *" if required else ""), opts, index=index)

            elif ftype in ("number", "money"):
                minv = float(f.get("min", 0.0) or 0.0)
                maxv = f.get("max", None)
                step = float(f.get("step", 1.0) or 1.0)

                try:
                    value = float(default)
                except:
                    value = minv

                # IMPORTANT: Streamlit requires value >= min_value
                value = max(value, minv)

                if maxv is not None:
                    maxv = float(maxv)
                    form_data[key] = st.number_input(
                        label + (" *" if required else ""),
                        min_value=minv,
                        max_value=maxv,
                        value=value,
                        step=step,
                        format="%.2f",
                    )
                else:
                    form_data[key] = st.number_input(
                        label + (" *" if required else ""),
                        min_value=minv,
                        value=value,
                        step=step,
                        format="%.2f",
                    )

            elif ftype == "textarea":
                form_data[key] = st.text_area(label + (" *" if required else ""), value=str(default or ""))

            else:
                form_data[key] = st.text_input(label + (" *" if required else ""), value=str(default or ""))

        submitted = st.form_submit_button("Submit")

    if submitted:
        payload = {"category": category, **form_data}

        # If seats is like 1.0, backend expects int (we made backend forgiving anyway)
        if "seats" in payload:
            try:
                if float(payload["seats"]).is_integer():
                    payload["seats"] = int(float(payload["seats"]))
            except:
                pass

        r = post_json("/items", payload)

        if r.status_code == 200:
            st.session_state.last_item = r.json()
            st.success("✅ Item submitted!")

            # fetch comps
            r2 = post_json("/comps", {"category": category, "name": payload.get("name", "")})
            if r2.status_code == 200:
                st.session_state.last_comps = r2.json()

        else:
            st.error("❌ Item submit failed.")
            # show compact error
            try:
                st.json(r.json())
            except:
                st.code(r.text)


# ---------------- Dashboard ----------------
comps = st.session_state.last_comps
if comps:
    st.subheader("📊 Price Comparison & Recommendation")

    items = comps.get("items", [])
    df = pd.DataFrame(items)

    if df.empty:
        st.info("No comps returned yet.")
    else:
        df["price_num"] = df["price"].apply(parse_price) if "price" in df.columns else None
        prices = df["price_num"].dropna()

        if len(prices) > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("Comps found", int(len(prices)))
            c2.metric("Median price", f"${prices.median():.0f}")
            c3.metric("Avg price", f"${prices.mean():.0f}")

            # simple bar chart counts by rounded price
            hist = prices.round(0).value_counts().sort_index()
            st.markdown("### 📈 Price distribution (simple bar)")
            st.bar_chart(hist)

            st.markdown("### 🎯 Price points (scatter)")
            scatter_df = pd.DataFrame({"index": range(1, len(prices) + 1), "price": prices.values})
            st.scatter_chart(scatter_df, x="index", y="price")

        st.markdown("### 🔎 Online comps (table)")
        show_cols = [c for c in ["title", "price", "source", "link"] if c in df.columns]
        st.dataframe(df[show_cols] if show_cols else df, use_container_width=True)
