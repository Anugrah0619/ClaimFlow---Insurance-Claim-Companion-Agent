import streamlit as st

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
    st.session_state.claim_tasks = [
        {"name": "Notify insurer", "status": "Pending"},
        {"name": "Upload hospital bill", "status": "Blocked"},
        {"name": "Upload discharge summary", "status": "Blocked"},
        {"name": "Submit claim form", "status": "Blocked"},
    ]

if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = set()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_status_badge(status):
    """Return a colored badge for each task status"""
    status_colors = {
        "Pending": "🟡",
        "Completed": "✅",
        "Blocked": "🔴",
        "At Risk": "🟠"
    }
    return f"{status_colors.get(status, '⚪')} {status}"

def update_task_status(task_name, new_status):
    """Update the status of a specific task"""
    for task in st.session_state.claim_tasks:
        if task["name"] == task_name:
            task["status"] = new_status
            break

def handle_document_upload(doc_type):
    """Handle document upload and update corresponding task status"""
    # Mock validation logic
    st.session_state.uploaded_documents.add(doc_type)
    
    # Map document types to task names
    doc_to_task = {
        "Hospital Bill": "Upload hospital bill",
        "Discharge Summary": "Upload discharge summary",
        "Claim Form": "Submit claim form"
    }
    
    if doc_type in doc_to_task:
        update_task_status(doc_to_task[doc_type], "Completed")
        st.success(f"✅ {doc_type} uploaded and validated successfully!")
        
        # Automatically update "Notify insurer" to completed after first document
        if len(st.session_state.uploaded_documents) == 1:
            update_task_status("Notify insurer", "Completed")
    else:
        st.warning("⚠️ Document type not recognized")

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("ClaimFlow – Insurance Claim Companion")
st.markdown("*We help you manage your insurance claim so you don't miss documents, deadlines, or money.*")
st.divider()

# ============================================================================
# SECTION 1: START CLAIM
# ============================================================================

if not st.session_state.claim_started:
    st.header("🚀 Start Your Claim")
    
    with st.container():
        # File uploader for policy
        policy_file = st.file_uploader(
            "Upload Insurance Policy (PDF)",
            type=["pdf"],
            help="Upload your insurance policy document"
        )
        
        # Incident description
        incident_desc = st.text_area(
            "Describe what happened (incident details)",
            height=150,
            placeholder="Please provide details about the incident..."
        )
        
        # Start Claim button
        if st.button("Start Claim", type="primary", use_container_width=True):
            if policy_file is not None and incident_desc.strip():
                # Save to session state
                st.session_state.policy_uploaded = True
                st.session_state.incident_description = incident_desc
                st.session_state.claim_started = True
                st.rerun()
            else:
                st.error("⚠️ Please upload a policy and describe the incident before starting the claim.")

# ============================================================================
# SECTION 2: CLAIM TRACKER (Shown only after claim started)
# ============================================================================

if st.session_state.claim_started:
    st.header("📊 Claim Progress Tracker")
    
    with st.container():
        # Display claim tasks as a checklist
        for idx, task in enumerate(st.session_state.claim_tasks):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{idx + 1}. {task['name']}**")
            with col2:
                st.markdown(get_status_badge(task['status']))
        
        # Progress bar
        completed_tasks = sum(1 for task in st.session_state.claim_tasks if task['status'] == 'Completed')
        total_tasks = len(st.session_state.claim_tasks)
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0
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
            # Document type dropdown
            doc_type = st.selectbox(
                "Select document type",
                options=["Hospital Bill", "Discharge Summary", "Claim Form"],
                help="Choose the type of document you want to upload"
            )
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload document",
                type=["pdf", "jpg", "png", "jpeg"],
                key=f"doc_uploader_{doc_type}"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            # Upload button
            if st.button("Upload Document", type="primary", use_container_width=True):
                if uploaded_file is not None:
                    handle_document_upload(doc_type)
                else:
                    st.warning("⚠️ Please select a file to upload")
    
    st.divider()
    
    # ============================================================================
    # SECTION 4: ACTION PANEL
    # ============================================================================
    
    st.header("⚡ Actions")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Generate Appeal Email", use_container_width=True):
                st.info("📧 Appeal email drafted successfully! Check your email for the draft.")
        
        with col2:
            if st.button("Escalate to Support", use_container_width=True):
                st.warning("🚨 Claim escalated to support team. You will receive a callback within 24 hours.")
        
        with col3:
            if st.button("Download Claim Summary", use_container_width=True):
                st.success("📥 Claim summary downloaded successfully!")
    
    st.divider()
    
    # ============================================================================
    # INCIDENT DETAILS (Reference)
    # ============================================================================
    
    with st.expander("View Incident Details"):
        st.markdown(f"**Incident Description:**")
        st.write(st.session_state.incident_description)
        st.markdown(f"**Policy Uploaded:** {'Yes' if st.session_state.policy_uploaded else 'No'}")
        st.markdown(f"**Documents Uploaded:** {', '.join(st.session_state.uploaded_documents) if st.session_state.uploaded_documents else 'None'}")
