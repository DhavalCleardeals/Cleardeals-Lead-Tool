import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Cleardeals Lead Tool", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Final Proper Version)")

# તમારી અપડેટેડ લોકેશન લિસ્ટ (૬૭ લોકેશન)
locations = [
    "Alandi", "Aundh", "Bakori", "Balewadi", "Baner", "Bavdhan", "Bhekraiwadi", "Bhosari", "Bibewad", "Blue Ridge",
    "Camp", "Chandan Nagar", "Chinchwad", "Dapodi", "Dhayri", "Dhanori", "Dighi", "Dudulgaon", "Fursungi", "Gahunje",
    "Ghorpadi", "Hadapsar", "Hinjewadi (All Phases)", "Kalyani Nagar", "Karvenagar", "Kasarwadi", "Katraj", "Keshavnagar",
    "Kesnand", "Khadki", "Kharadi", "Kiwale", "Koregaon Park", "Kondhwa", "Kothrud", "Lohegaon", "Lodha Belmondo", "Magarpatta",
    "Manjari", "Mohammadwadi", "Moshi", "Mundhwa", "Nibm", "Nigdi", "Pashan", "Pimple Gurav", "Pimple Nilakh", "Pimple Saudagar",
    "Pimpri", "Pisoli", "Pride World City", "Punawale", "Rahatani", "Ravet", "Sangvi", "Sasane Nagar", "Shikrapur", "Sus",
    "Tathawade", "Tingre Nagar", "Undri", "Viman Nagar", "Vishrantwadi", "Wadgaon Sheri", "Wagholi", "Wakad", "Warje"
]

def load_file(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    return None

def clean_txt(text):
    return re.sub(r'[^a-z0-9]', '', str(text).lower().strip())

def clean_num(num):
    return re.sub(r'[^0-9]', '', str(num).strip())

def process_leads(df_rent, df_sale, main_list):
    # Cleaning
    df_rent['area_clean'] = df_rent['area'].apply(clean_txt)
    df_sale['area_clean'] = df_sale['area'].apply(clean_txt)
    
    if 'owner_contact' in df_rent.columns:
        df_rent['contact_clean'] = df_rent['owner_contact'].apply(clean_num)
    if 'owner_contact' in df_sale.columns:
        df_sale['contact_clean'] = df_sale['owner_contact'].apply(clean_num)

    main_rows = []
    r_matched_idx = set()
    s_matched_idx = set()

    for i, loc in enumerate(main_list, 1):
        term = clean_txt(loc.split('(')[0])
        
        # Matching
        if "hinjewadi" in term:
            r_mask = df_rent['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
            s_mask = df_sale['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
        else:
            r_mask = df_rent['area_clean'].str.contains(term, na=False)
            s_mask = df_sale['area_clean'].str.contains(term, na=False)
            
        r_df = df_rent[r_mask]
        s_df = df_sale[s_mask]
        
        r_matched_idx.update(r_df.index.tolist())
        s_matched_idx.update(s_df.index.tolist())
        
        # Duplicates
        r_dup = r_df.duplicated(subset=['contact_clean']).sum() if 'contact_clean' in r_df.columns else 0
        s_dup = s_df.duplicated(subset=['contact_clean']).sum() if 'contact_clean' in s_df.columns else 0
        
        main_rows.append({
            'Sr. No.': i, 'Location Name': loc,
            'No. of Rental Property Leads': len(r_df),
            'No. of Resale Property Leads': len(s_df),
            'Total Leads': len(r_df) + len(s_df),
            'Duplicate data Rental Property Leads': r_dup,
            'Duplicate data Resale Property Leads': s_dup
        })

    # Extra areas
    r_ex = df_rent[~df_rent.index.isin(r_matched_idx)]
    s_ex = df_sale[~df_sale.index.isin(s_matched_idx)]
    
    r_ex_sum = r_ex.groupby('area').size().reset_index(name='Rental Leads')
    s_ex_sum = s_ex.groupby('area').size().reset_index(name='Resale Leads')
    
    extra_df = pd.merge(r_ex_sum, s_ex_sum, on='area', how='outer').fillna(0)
    extra_df['Total Leads'] = extra_df['Rental Leads'] + extra_df['Resale Leads']
    extra_df.rename(columns={'area': 'Extra Area Name'}, inplace=True)
    
    return pd.DataFrame(main_rows), extra_df

# UI Section
f_rent = st.file_uploader("1. Rental Leads Upload (CSV/Excel)", type=['csv', 'xlsx', 'xls'])
f_sale = st.file_uploader("2. Resale Leads Upload (CSV/Excel)", type=['csv', 'xlsx', 'xls'])

if st.button("Generate Excel Report"):
    if f_rent and f_sale:
        df_rent = load_file(f_rent)
        df_sale = load_file(f_sale)
        
        df_m, df_e = process_leads(df_rent, df_sale, locations)
        
        # Total Row
        t_row = pd.DataFrame([[
            'Total', 'All Locations', df_m['No. of Rental Property Leads'].sum(), 
            df_m['No. of Resale Property Leads'].sum(), df_m['Total Leads'].sum(),
            df_m['Duplicate data Rental Property Leads'].sum(),
            df_m['Duplicate data Resale Property Leads'].sum()
        ]], columns=df_m.columns)
        
        df_final = pd.concat([df_m, t_row], ignore_index=True)
        
        st.success("✅ રિપોર્ટ તૈયાર છે!")
        st.dataframe(df_final)
        
        # Excel Download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Summary')
            if not df_e.empty:
                # Add gap and Extra Locations in same sheet
                df_e.to_excel(writer, index=False, sheet_name='Summary', startrow=len(df_final)+4)
                
        st.download_button("📥 Download Final Excel", data=output.getvalue(), file_name="Cleardeals_Summary.xlsx")
