import streamlit as st
import pandas as pd
from io import BytesIO
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="UPI VPA Generator Pro",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'custom_handles' not in st.session_state:
    st.session_state['custom_handles'] = []
if 'vpas' not in st.session_state:
    st.session_state['vpas'] = []
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Default UPI handles
DEFAULT_HANDLES = [
    'paytm', 'ybl', 'okaxis', 'oksbi', 'okicici', 'okhdfc',
    'ibl', 'axl', 'apl', 'barodampay', 'cnrb', 'federal',
    'ikwik', 'indus', 'kmbl', 'pockets', 'timecosmos',
    'yapl', 'airtel', 'fbl', 'hsbc', 'icici', 'kotak',
    'pingpay', 'sib', 'unionbank', 'jupiter', 'fbpe',
    'aubank', 'bandhan', 'citi', 'dbs', 'equitas',
    'idfc', 'indianbank', 'iob', 'jio', 'kvb',
    'lvb', 'mybank', 'niyogin', 'obc', 'pnb',
    'rbl', 'scb', 'synb', 'tjsb', 'uco',
    'unionbankofindia', 'united', 'vijb', 'yesbank', 'postbank'
]

def validate_phone_number(number):
    """Validate if the number is a 10-digit phone number"""
    number = str(number).strip()
    return len(number) == 10 and number.isdigit()

def generate_vpas(phone_numbers, selected_handles, custom_format=None):
    """Generate VPA combinations with optional custom format"""
    vpas = []
    for number in phone_numbers:
        if validate_phone_number(number):
            for handle in selected_handles:
                if custom_format:
                    vpa = custom_format.replace('{number}', number).replace('{handle}', handle)
                else:
                    vpa = f"{number}@{handle}"
                vpas.append(vpa)
    return vpas

def save_to_history(phone_numbers, handles, vpas_count):
    """Save generation to history"""
    st.session_state['history'].append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'phone_count': len(phone_numbers),
        'handle_count': len(handles),
        'vpas_count': vpas_count
    })

# Header
st.markdown('<div class="main-header"><h1>💳 UPI VPA Generator Pro</h1><p>Advanced VPA Generation with Custom TPAPs</p></div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Tab for settings
    tab1, tab2, tab3 = st.tabs(["🎯 Handles", "➕ Custom", "📊 History"])
    
    with tab1:
        st.subheader("Select UPI Handles")
        
        # Quick select options
        select_all = st.checkbox("Select All Handles", value=True)
        
        if select_all:
            selected_handles = DEFAULT_HANDLES.copy()
        else:
            # Category-wise selection
            categories = {
                "Popular Banks": ['ybl', 'paytm', 'okaxis', 'oksbi', 'okicici', 'okhdfc'],
                "Payment Apps": ['paytm', 'ybl', 'airtel', 'jio', 'jupiter'],
                "All Banks": [h for h in DEFAULT_HANDLES if h not in ['paytm', 'ybl', 'airtel', 'jio']]
            }
            
            category = st.selectbox("Choose Category:", list(categories.keys()))
            selected_handles = st.multiselect(
                "Select Handles:",
                options=DEFAULT_HANDLES,
                default=categories[category]
            )
        
        # Add custom handles to selection
        if st.session_state['custom_handles']:
            add_custom = st.checkbox("Include Custom Handles", value=True)
            if add_custom:
                selected_handles.extend(st.session_state['custom_handles'])
        
        st.info(f"✅ **{len(selected_handles)}** handles selected")
    
    with tab2:
        st.subheader("Add Custom TPAPs")
        
        # Single handle addition
        new_handle = st.text_input("Enter TPAP Handle:", placeholder="e.g., mybank")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add", use_container_width=True):
                if new_handle and new_handle not in DEFAULT_HANDLES and new_handle not in st.session_state['custom_handles']:
                    st.session_state['custom_handles'].append(new_handle)
                    st.success(f"Added: {new_handle}")
                    st.rerun()
                elif not new_handle:
                    st.error("Enter a handle")
                else:
                    st.warning("Already exists")
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state['custom_handles'] = []
                st.rerun()
        
        # Bulk addition
        st.markdown("---")
        bulk_handles = st.text_area(
            "Bulk Add (one per line):",
            height=100,
            placeholder="mybank1\nmybank2\nmybank3"
        )
        
        if st.button("📥 Add Bulk", use_container_width=True):
            if bulk_handles:
                new_handles = [h.strip() for h in bulk_handles.split('\n') if h.strip()]
                added = 0
                for h in new_handles:
                    if h not in DEFAULT_HANDLES and h not in st.session_state['custom_handles']:
                        st.session_state['custom_handles'].append(h)
                        added += 1
                st.success(f"Added {added} new handles")
                st.rerun()
        
        # Display custom handles
        if st.session_state['custom_handles']:
            st.markdown("**Custom Handles:**")
            for i, handle in enumerate(st.session_state['custom_handles']):
                col1, col2 = st.columns([3, 1])
                col1.write(f"• {handle}")
                if col2.button("❌", key=f"del_{i}"):
                    st.session_state['custom_handles'].pop(i)
                    st.rerun()
    
    with tab3:
        st.subheader("Generation History")
        if st.session_state['history']:
            for i, record in enumerate(reversed(st.session_state['history'][-5:])):
                with st.expander(f"#{len(st.session_state['history'])-i} - {record['timestamp']}"):
                    st.write(f"📱 Phones: {record['phone_count']}")
                    st.write(f"🏦 Handles: {record['handle_count']}")
                    st.write(f"📊 VPAs: {record['vpas_count']}")
        else:
            st.info("No history yet")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state['history'] = []
            st.rerun()

# Warning box
st.warning("""
⚠️ **Important Notice:**
- Generated IDs must be verified **manually** in UPI apps
- Do NOT use for automated scraping or API abuse
- Respect privacy and terms of service
- Only for legitimate purposes
""")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📱 Input Phone Numbers")
    
    input_method = st.radio(
        "Choose input method:",
        ["📝 Text Area", "📁 File Upload", "🔢 Range Generator"],
        horizontal=True
    )
    
    phone_numbers = []
    
    if input_method == "📝 Text Area":
        phone_input = st.text_area(
            "Enter phone numbers (one per line):",
            height=250,
            placeholder="9876543210\n9123456789\n9988776655"
        )
        if phone_input:
            phone_numbers = [line.strip() for line in phone_input.split('\n') if line.strip()]
    
    elif input_method == "📁 File Upload":
        uploaded_file = st.file_uploader(
            "Upload a text/CSV file with phone numbers",
            type=['txt', 'csv']
        )
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            phone_numbers = [line.strip().split(',')[0] for line in content.split('\n') if line.strip()]
    
    else:  # Range Generator
        st.info("Generate sequential numbers for testing")
        col_a, col_b = st.columns(2)
        with col_a:
            start_num = st.text_input("Start Number:", "9000000000")
        with col_b:
            count = st.number_input("Count:", min_value=1, max_value=100, value=10)
        
        if st.button("🎲 Generate Range"):
            if validate_phone_number(start_num):
                base = int(start_num)
                phone_numbers = [str(base + i) for i in range(count)]
                st.success(f"Generated {count} numbers")
    
    # Validation summary
    if phone_numbers:
        valid_numbers = [num for num in phone_numbers if validate_phone_number(num)]
        invalid_numbers = [num for num in phone_numbers if not validate_phone_number(num)]
        
        col_a, col_b = st.columns(2)
        col_a.metric("✅ Valid", len(valid_numbers))
        col_b.metric("❌ Invalid", len(invalid_numbers))
        
        if invalid_numbers:
            with st.expander("⚠️ View Invalid Numbers"):
                st.write(invalid_numbers)

with col2:
    st.subheader("⚙️ Advanced Options")
    
    # Custom format
    use_custom_format = st.checkbox("🎨 Use Custom VPA Format")
    custom_format = None
    
    if use_custom_format:
        custom_format = st.text_input(
            "Custom Format:",
            value="{number}@{handle}",
            help="Use {number} and {handle} as placeholders"
        )
        st.code(f"Example: {custom_format.replace('{number}', '9876543210').replace('{handle}', 'paytm')}")
    
    # Prefix/Suffix options
    col_a, col_b = st.columns(2)
    with col_a:
        add_prefix = st.text_input("➕ Prefix (optional):", placeholder="e.g., +91")
    with col_b:
        add_suffix = st.text_input("➕ Suffix (optional):", placeholder="e.g., -verified")
    
    # Duplicate removal
    remove_duplicates = st.checkbox("🔄 Remove Duplicates", value=True)
    
    # Sort options
    sort_option = st.selectbox(
        "📑 Sort Output:",
        ["No Sorting", "By Phone Number", "By Handle", "Alphabetically"]
    )

# Generate Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 Generate VPAs", type="primary", use_container_width=True):
        if not phone_numbers:
            st.error("❌ Please enter at least one phone number")
        elif not selected_handles:
            st.error("❌ Please select at least one UPI handle")
        else:
            with st.spinner("🔄 Generating VPAs..."):
                valid_numbers = [num for num in phone_numbers if validate_phone_number(num)]
                
                # Apply prefix/suffix
                if add_prefix:
                    valid_numbers = [add_prefix + num for num in valid_numbers]
                if add_suffix:
                    valid_numbers = [num + add_suffix for num in valid_numbers]
                
                vpas = generate_vpas(valid_numbers, selected_handles, custom_format)
                
                # Remove duplicates
                if remove_duplicates:
                    vpas = list(set(vpas))
                
                # Sort
                if sort_option == "By Phone Number":
                    vpas.sort(key=lambda x: x.split('@')[0])
                elif sort_option == "By Handle":
                    vpas.sort(key=lambda x: x.split('@')[1] if '@' in x else x)
                elif sort_option == "Alphabetically":
                    vpas.sort()
                
                st.session_state['vpas'] = vpas
                st.session_state['valid_numbers'] = [num.replace(add_prefix, '').replace(add_suffix, '') for num in valid_numbers]
                
                # Save to history
                save_to_history(valid_numbers, selected_handles, len(vpas))

# Display Results
if st.session_state['vpas']:
    vpas = st.session_state['vpas']
    valid_numbers = st.session_state.get('valid_numbers', [])
    
    st.markdown("---")
    st.markdown('<div class="success-box"><h3>✅ Generation Complete!</h3></div>', unsafe_allow_html=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📱 Phone Numbers", len(valid_numbers))
    col2.metric("🏦 UPI Handles", len(selected_handles))
    col3.metric("📊 Total VPAs", len(vpas))
    col4.metric("💾 Unique VPAs", len(set(vpas)))
    
    # Display tabs
    tab1, tab2, tab3 = st.tabs(["📋 Table View", "📝 List View", "💾 Download"])
    
    with tab1:
        # Create DataFrame
        df_data = []
        for vpa in vpas:
            if '@' in vpa:
                parts = vpa.split('@')
                df_data.append({
                    'Phone Number': parts[0],
                    'UPI Handle': parts[1],
                    'Full VPA': vpa
                })
        df = pd.DataFrame(df_data)
        
        # Search and filter
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            search_term = st.text_input("🔍 Search VPAs:", placeholder="Enter phone or handle")
        with search_col2:
            filter_handle = st.selectbox("Filter by Handle:", ["All"] + list(df['UPI Handle'].unique()))
        
        # Apply filters
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[filtered_df['Full VPA'].str.contains(search_term, case=False)]
        if filter_handle != "All":
            filtered_df = filtered_df[filtered_df['UPI Handle'] == filter_handle]
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        st.info(f"Showing {len(filtered_df)} of {len(df)} VPAs")
    
    with tab2:
        search_list = st.text_input("🔍 Search in list:", placeholder="Type to filter")
        
        display_vpas = vpas
        if search_list:
            display_vpas = [vpa for vpa in vpas if search_list.lower() in vpa.lower()]
        
        st.text_area(
            f"VPA List ({len(display_vpas)} items):",
            value='\n'.join(display_vpas),
            height=400
        )
        
        # Quick copy button
        if st.button("📋 Copy All to Clipboard"):
            st.code('\n'.join(display_vpas))
            st.success("✅ VPAs ready to copy from above!")
    
    with tab3:
        st.subheader("💾 Download Generated VPAs")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # TXT Download
            txt_data = '\n'.join(vpas)
            st.download_button(
                label="📄 Download TXT",
                data=txt_data,
                file_name=f"upi_vpas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # CSV Download
            df = pd.DataFrame([vpa.split('@') for vpa in vpas if '@' in vpa], 
                            columns=['phone_number', 'upi_handle'])
            df['full_vpa'] = vpas
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"upi_vpas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # Excel Download
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='VPAs')
            excel_buffer.seek(0)
            
            st.download_button(
                label="📑 Download Excel",
                data=excel_buffer,
                file_name=f"upi_vpas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # JSON Download
        json_data = json.dumps({
            'generated_at': datetime.now().isoformat(),
            'total_vpas': len(vpas),
            'vpas': vpas
        }, indent=2)
        
        st.download_button(
            label="📦 Download JSON",
            data=json_data,
            file_name=f"upi_vpas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p><strong>UPI VPA Generator Pro v2.0</strong></p>
    <p>Use responsibly and ethically. Manual verification only.</p>
    <p>⚠️ This tool is for educational purposes only</p>
</div>
""", unsafe_allow_html=True)
