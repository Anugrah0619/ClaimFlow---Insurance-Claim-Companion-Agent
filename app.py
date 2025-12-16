import streamlit as st
from agent.workflow_generator import generate_claim_tasks
from services.policy_reader import extract_policy_rules
from agent.document_validator import run_document_validation_agent

from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ClaimFlow – Insurance Claim Companion",
    page_icon="📋",
    layout="wide"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "claim_started" not in st.session_state:
    st.session_state.claim_started = False

if "policy_uploaded" not in st.session_state:
    st.session_state.policy_uploaded = False

if "incident_description" not in st.session_state:
    st.session_state.incident_description = ""

if "claim_tasks" not in st.session_state:
    st.session_state.claim_tasks = []

if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = set()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_status_badge(status):
    status_colors = {
        "Pending": "🟡",
        "Completed": "✅",
        "Blocked": "🔴",
        "At Risk": "🟠"
    }
    return f"{status_colors.get(status, '⚪')} {status}"

def update_task_status(task_name, new_status):
    for task in st.session_state.claim_tasks:
        if task["name"] == task_name:
            task["status"] = new_status
            break

def handle_document_upload(task_name, uploaded_file):
    decision = run_document_validation_agent(
        task_name=task_name,
        file_name=uploaded_file.name
    )

    accepted = decision.get("accepted", False)
    reason = decision.get("reason", "No reason provided")

    if accepted:
        update_task_status(task_name, "Completed")
        st.success(f"✅ {task_name} accepted: {reason}")

        # Auto-complete Notify insurer
        update_task_status("Notify insurer", "Completed")
    else:
        update_task_status(task_name, "Blocked")
        st.error(f"❌ {task_name} rejected: {reason}")

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("ClaimFlow – Insurance Claim Companion")
st.markdown(
    "*We help you manage your insurance claim so you don't miss documents, deadlines, or money.*"
)
st.divider()

# ============================================================================
# SECTION 1: START CLAIM
# ============================================================================

if not st.session_state.claim_started:
    st.header("🚀 Start Your Claim")

    with st.container():
        policy_file = st.file_uploader(
            "Upload Insurance Policy (PDF)",
            type=["pdf"],
            help="Upload your insurance policy document"
        )

        incident_desc = st.text_area(
            "Describe what happened (incident details)",
            height=150,
            placeholder="Please provide details about the incident..."
        )

        if st.button("Start Claim", type="primary", use_container_width=True):
            if policy_file is not None and incident_desc.strip():

                # 🔥 Reset claim-specific state (important)
                st.session_state.uploaded_documents = set()
                st.session_state.claim_tasks = []

                # Agent step 1: read policy (stub)
                policy_text = "dummy policy text"
                policy_rules = extract_policy_rules(policy_text)

                # Agent step 2: generate workflow
                tasks = generate_claim_tasks(policy_rules, incident_desc)

                # Store agent-generated tasks
                st.session_state.claim_tasks = [
                    {"name": task.name, "status": task.status}
                    for task in tasks
                ]

                st.session_state.policy_uploaded = True
                st.session_state.incident_description = incident_desc
                st.session_state.claim_started = True

                st.rerun()
            else:
                st.error(
                    "⚠️ Please upload a policy and describe the incident before starting the claim."
                )

# ============================================================================
# SECTION 2: CLAIM TRACKER
# ============================================================================

if st.session_state.claim_started:
    st.header("📊 Claim Progress Tracker")

    with st.container():
        for idx, task in enumerate(st.session_state.claim_tasks):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{idx + 1}. {task['name']}**")
            with col2:
                st.markdown(get_status_badge(task["status"]))

        completed_tasks = sum(
            1 for task in st.session_state.claim_tasks
            if task["status"] == "Completed"
        )
        total_tasks = len(st.session_state.claim_tasks)
        progress = completed_tasks / total_tasks if total_tasks else 0

        st.progress(progress)
        st.caption(f"Progress: {completed_tasks}/{total_tasks} tasks completed")

    st.divider()

    # ============================================================================
    # SECTION 3: DOCUMENT UPLOAD
    # ============================================================================

    st.header("📄 Document Upload")

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            # Build upload options dynamically from agent-generated tasks
            document_tasks = [
                task["name"]
                for task in st.session_state.claim_tasks
                if task["name"].lower().startswith("upload")
                and task["status"] != "Completed"
            ]

            if document_tasks:
                selected_task = st.selectbox(
                    "Select document type",
                    document_tasks
                )

                uploaded_file = st.file_uploader(
                    "Upload document",
                    type=["pdf", "jpg", "png", "jpeg"],
                    key=f"doc_{selected_task}"
                )
            else:
                selected_task = None
                st.info("✅ All required documents have been uploaded.")

        with col2:
            st.write("")
            st.write("")
            if st.button("Upload Document", type="primary", use_container_width=True):
                if selected_task and uploaded_file:
                    handle_document_upload(selected_task, uploaded_file)
                elif not selected_task:
                    st.info("No pending documents to upload.")
                else:
                    st.warning("⚠️ Please select a file to upload")

    st.divider()

    # ============================================================================
    # SECTION 4: ACTION PANEL
    # ============================================================================

    st.header("⚡ Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Generate Appeal Email", use_container_width=True):
            st.info("📧 Appeal email drafted successfully!")

    with col2:
        if st.button("Escalate to Support", use_container_width=True):
            st.warning("🚨 Claim escalated to support team.")

    with col3:
        if st.button("Download Claim Summary", use_container_width=True):
            st.success("📥 Claim summary downloaded!")

    st.divider()

    # ============================================================================
    # INCIDENT DETAILS
    # ============================================================================

    with st.expander("View Incident Details"):
        st.markdown("**Incident Description:**")
        st.write(st.session_state.incident_description)

        st.markdown(
            f"**Policy Uploaded:** {'Yes' if st.session_state.policy_uploaded else 'No'}"
        )

        uploaded_docs = (
            ", ".join(st.session_state.uploaded_documents)
            if st.session_state.uploaded_documents else "None"
        )
        st.markdown(f"**Documents Uploaded:** {uploaded_docs}")