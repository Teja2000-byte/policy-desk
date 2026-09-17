import json
import os
from datetime import datetime

import streamlit as st

from src.ui_client import APIError, request_api

st.set_page_config(page_title="Policy Desk", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """<style>
 .stApp {background:#f7f8fa;}
 .block-container {max-width:1180px;padding-top:4.5rem;padding-bottom:3rem;}
 [data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #e3e8ed;}
 h1,h2,h3 {letter-spacing:-0.035em;}
 h1 {font-size:2.7rem!important;font-weight:650!important;}
 .eyebrow {font-size:12px;letter-spacing:0.14em;color:#087e76;font-weight:750;}
 .subtitle {font-size:17px;color:#667085;max-width:670px;line-height:1.6;margin-bottom:28px;}
 .brand {font-size:25px;font-weight:750;color:#123a40;letter-spacing:-1px;margin:12px 0 2px;}
 .brand-note {color:#7b8693;font-size:12px;margin-bottom:28px;}
 [data-testid="stForm"] {background:#fff;border:1px solid #dfe5ec;border-radius:14px;padding:24px;}
 [data-testid="stMetric"] {background:#fff;border:1px solid #e3e8ed;border-radius:12px;padding:16px;}
 .stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"] {border-radius:8px;}
 .quiet {font-size:13px;color:#7b8693;line-height:1.65;}
 .stAlert {border-radius:10px;}
 </style>""",
    unsafe_allow_html=True,
)

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def api(method, path, payload=None, params=None):
    try:
        return request_api(
            method,
            path,
            base_url=BASE_URL,
            token=st.session_state.get("token"),
            payload=payload,
            params=params,
        )
    except APIError as exc:
        if exc.status == 401 and st.session_state.get("token"):
            st.session_state.clear()
            st.session_state["notice"] = "Your session expired. Please sign in again."
            st.rerun()
        raise


def display_result(ticket):
    decision = ticket["decision"]
    st.markdown("---")
    st.caption(f"DECISION / TICKET #{ticket['id']:04d}")
    title = decision["action"].replace("_", " ").capitalize()
    if decision["action"] == "NEEDS_MORE_INFORMATION":
        st.warning(title, icon="💬")
    else:
        st.success(title, icon="✅")
    st.write(decision["reason"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Model confidence", f"{decision['confidence']:.0%}")
    c2.metric("Cited policies", len(decision["sources"]))
    c3.metric("Decision time", f"{decision['latency_ms'] / 1000:.1f}s")
    st.caption(
        "Confidence is the model’s estimate, not a measured probability. Review the evidence before acting."
    )
    if decision["missing_information"]:
        st.markdown("**Ask the customer**")
        for question in decision["missing_information"]:
            st.write("• " + question)
    st.markdown("#### Policy evidence")
    context = {chunk["chunk_id"]: chunk for chunk in decision["retrieved_context"]}
    if not decision["evidence"]:
        st.caption("No policy evidence was cited. More information is needed before recommending an action.")
    for index, evidence in enumerate(decision["evidence"], 1):
        chunk = context[evidence["chunk_id"]]
        with st.expander(f"{index:02d} · {chunk['source']} · {evidence['chunk_id']}", expanded=index == 1):
            st.write(evidence["quote"])
            st.caption("Quote verified against the retrieved policy text.")
    with st.expander("Decision details"):
        st.write("**Submitted ticket**")
        st.write(ticket["message"])
        st.json(
            {
                key: ticket[key]
                for key in (
                    "order_value_inr",
                    "days_since_delivery",
                    "days_since_dispatch",
                    "product_type",
                    "opened_status",
                    "order_status",
                )
            }
        )
        st.caption(
            f"Model: {decision['model']} · Policy version: {decision['policy_version'][:12]} · Saved: {decision['created_at']}"
        )
        st.markdown("**Retrieved context**")
        for chunk in decision["retrieved_context"]:
            st.caption(f"{chunk['chunk_id']} · cosine similarity {chunk['similarity']:.3f}")
            st.text(chunk["text"])
    st.download_button(
        "Download decision JSON",
        json.dumps(ticket, indent=2, ensure_ascii=False),
        file_name=f"decision-{ticket['id']}.json",
        mime="application/json",
        key=f"download-{ticket['id']}",
    )


with st.sidebar:
    st.markdown(
        '<div class="brand">◈ Policy Desk</div><div class="brand-note">SUPPORT DECISION ASSISTANT</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("token"):
        st.caption("SIGNED IN AS")
        st.write(st.session_state.get("email", ""))
        page = st.radio("Workspace", ["New decision", "History"], label_visibility="collapsed")
        st.divider()
        if st.button("Sign out", width="stretch"):
            st.session_state.clear()
            st.rerun()
    else:
        page = "Account"
        st.markdown("**Every recommendation, explained.**")
        st.caption("Review the proposed action, understand the policy behind it, and revisit your decisions.")
    st.divider()
    try:
        health = api("GET", "/health")
        st.caption("● Decision service online")
        if health["gemini_configured"]:
            st.caption("Gemini key configured")
        else:
            st.warning("Gemini setup needed. Add your key to the backend .env and restart.")
    except APIError:
        st.caption("○ Decision service offline")
    st.markdown(
        '<p class="quiet">Recommendations for human review.<br>No refunds or replacements are executed.</p>',
        unsafe_allow_html=True,
    )


if page == "Account":
    st.markdown('<div class="eyebrow">EVIDENCE BEFORE ACTION</div>', unsafe_allow_html=True)
    st.title("Clear decisions, grounded in policy.")
    st.markdown(
        '<div class="subtitle">Turn a support ticket into a clear next step, with the policy evidence to back it up.</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("notice"):
        st.info(st.session_state.pop("notice"))
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])
        for tab, register in [(login_tab, False), (register_tab, True)]:
            with tab:
                with st.form("register" if register else "login", clear_on_submit=True):
                    st.subheader("Create your workspace" if register else "Welcome back")
                    email = st.text_input("Email", key=f"email-{register}", placeholder="you@example.com")
                    password = st.text_input(
                        "Password", type="password", key=f"password-{register}", help="Use 8–128 characters."
                    )
                    submitted = st.form_submit_button(
                        "Create account" if register else "Sign in", type="primary", width="stretch"
                    )
                if submitted:
                    try:
                        payload = {"email": email, "password": password}
                        if register:
                            api("POST", "/register", payload)
                        token = api("POST", "/login", payload)
                        st.session_state["token"] = token["access_token"]
                        st.session_state["email"] = api("GET", "/me")["email"]
                        st.rerun()
                    except APIError as exc:
                        st.error(str(exc))
    with right:
        st.markdown("### A simpler support workflow")
        st.markdown("**01 · Describe the issue**\n\nAdd the customer’s message and the order facts you know.")
        st.markdown(
            "**02 · Review the evidence**\n\nSee the recommended action, reasoning, and exact policy quotes."
        )
        st.markdown(
            "**03 · Keep the context**\n\nYour tickets and decisions stay together in your account’s history."
        )

elif page == "New decision":
    st.markdown('<div class="eyebrow">YOUR WORKSPACE / NEW DECISION</div>', unsafe_allow_html=True)
    st.title("What does the customer need?")
    st.markdown(
        '<div class="subtitle">Describe the issue and add known order details. Leave anything you do not know blank.</div>',
        unsafe_allow_html=True,
    )
    examples = {
        "Start with a blank ticket": {},
        "Damaged delivery · ₹3,500": {
            "message": "My ₹3,500 order arrived damaged yesterday.",
            "order_value_inr": 3500.0,
            "days_since_delivery": 1,
            "product_type": "non_food",
            "opened_status": "opened",
            "order_status": "delivered",
        },
        "Delayed shipment · 9 days": {
            "message": "My parcel has still not arrived and it was dispatched 9 days ago.",
            "days_since_dispatch": 9,
            "order_status": "dispatched",
        },
        "Unopened return · 10 days": {
            "message": "I changed my mind about this unopened non-food product. It arrived 10 days ago.",
            "days_since_delivery": 10,
            "product_type": "non_food",
            "opened_status": "unopened",
            "order_status": "delivered",
        },
        "Missing information": {
            "message": "I want to return this.",
            "order_value_inr": 900.0,
            "order_status": "delivered",
        },
    }
    selected = st.selectbox("Try an example", list(examples))
    if st.session_state.get("selected_example") != selected:
        st.session_state["selected_example"] = selected
        defaults = {
            "message": "",
            "order_value_inr": None,
            "days_since_delivery": None,
            "days_since_dispatch": None,
            "product_type": "unknown",
            "opened_status": "unknown",
            "order_status": "unknown",
        }
        defaults.update(examples[selected])
        for key, value in defaults.items():
            st.session_state[key] = value
        st.session_state.pop("latest_ticket", None)
    with st.form("decision-form"):
        st.markdown("#### Customer’s message")
        st.text_area(
            "Support ticket",
            key="message",
            height=120,
            max_chars=5000,
            placeholder="What happened, and what help is the customer asking for?",
            label_visibility="collapsed",
        )
        st.markdown("#### Order details")
        a, b, c = st.columns(3)
        a.number_input(
            "Order value (₹)",
            min_value=0.0,
            max_value=10_000_000.0,
            value=None,
            step=100.0,
            key="order_value_inr",
            placeholder="Unknown",
        )
        b.number_input(
            "Days since delivery",
            min_value=0,
            max_value=3650,
            value=None,
            step=1,
            key="days_since_delivery",
            placeholder="Unknown",
        )
        c.number_input(
            "Days since dispatch",
            min_value=0,
            max_value=3650,
            value=None,
            step=1,
            key="days_since_dispatch",
            placeholder="Unknown",
        )
        a, b, c = st.columns(3)
        a.selectbox(
            "Product type",
            ["unknown", "food", "non_food", "mixed"],
            key="product_type",
            format_func=lambda x: x.replace("_", " ").capitalize(),
        )
        b.selectbox(
            "Package status",
            ["unknown", "unopened", "opened"],
            key="opened_status",
            format_func=str.capitalize,
        )
        c.selectbox(
            "Order status",
            ["unknown", "processing", "not_dispatched", "dispatched", "delivered"],
            key="order_status",
            format_func=lambda x: x.replace("_", " ").capitalize(),
        )
        st.caption("The ticket and order facts are sent to Gemini to generate a recommendation.")
        submit = st.form_submit_button("Generate decision →", type="primary", width="stretch")
    if submit:
        st.session_state.pop("latest_ticket", None)
        payload = {
            key: st.session_state[key]
            for key in (
                "message",
                "order_value_inr",
                "days_since_delivery",
                "days_since_dispatch",
                "product_type",
                "opened_status",
                "order_status",
            )
        }
        try:
            with st.spinner("Retrieving policies, checking the ticket, and preparing a decision…"):
                st.session_state["latest_ticket"] = api("POST", "/tickets", payload)
        except APIError as exc:
            st.error(str(exc))
    if st.session_state.get("latest_ticket"):
        display_result(st.session_state["latest_ticket"])

else:
    st.markdown('<div class="eyebrow">YOUR WORKSPACE / HISTORY</div>', unsafe_allow_html=True)
    st.title("Every decision, in context.")
    st.markdown(
        '<div class="subtitle">Revisit your tickets, recommendations, and the evidence behind them.</div>',
        unsafe_allow_html=True,
    )
    try:
        page_number = st.number_input("Page", min_value=1, value=1, step=1)
        history = api("GET", "/tickets", params={"limit": 10, "offset": (page_number - 1) * 10})
        st.caption(f"{history['total']} saved decisions · newest first")
        if not history["items"]:
            st.info("No decisions on this page. Create your first decision or choose an earlier page.")
        else:
            by_id = {item["id"]: item for item in history["items"]}
            selected_id = st.selectbox(
                "Choose a ticket",
                list(by_id),
                format_func=lambda value: (
                    f"#{value:04d} · {datetime.fromisoformat(by_id[value]['created_at']).strftime('%d %b %H:%M')} · {by_id[value]['message'][:80]}"
                ),
            )
            display_result(api("GET", f"/tickets/{selected_id}"))
    except APIError as exc:
        st.error(str(exc))
