import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Separate Duplicate Counts)")

# તમારી ૬૫ લોકેશનની લિસ્ટ
locations = [
    "Alandi", "Aundh", "Bakori", "Balewadi", "Baner", "Bavdhan", "Bhekraiwadi", "Bhosari", "Bibewad", "Blue Ridge",
    "Camp", "Chandan Nagar", "Chinchwad", "Dapodi", "Dhayri", "Dhanori", "Dighi", "Dudulgaon", "Fursungi", "Gahunje",
    "Ghorpadi", "Hadapsar", "Hinjewadi (All Phases)", "Kalyani Nagar", "Karvenagar", "Kasarwadi", "Katraj", "Keshavnagar",
    "Kesnand", "Khadki", "Kharadi", "Kiwale", "Koregaon Park", "Kondhwa", "Kothrud", "Lohegaon", "Lodha Belmondo", "Magarpatta",
    "Manjari", "Mohammadwadi", "Moshi", "Mundhwa", "Nibm", "Nigdi", "Pashan", "Pimple Gurav", "Pimple Nilakh", "Pimple Saudagar",
    "Pimpri", "Pisoli", "Pride World City", "Punawale", "Rahatani", "Ravet", "Sangvi", "Sasane Nagar", "Shikrapur", "Sus",
    "Tathawade", "Tingre Nagar", "Undri", "Viman Nagar", "Vishrantwadi", "Wadgaon Sheri", "Wagholi", "Wakad", "Warje"
]

def clean(text):
    return re.sub(r'[^a-z0-9]', '', str(text).lower().strip())

def process_data(df_rent, df_sale, main_locations):
    df_rent['area_clean'] = df_rent['area'].apply(clean)
    df_sale['area_clean'] = df_sale['area'].apply(clean)
    
    main_rows = []
    matched_rent_idx = set()
    matched_sale_idx = set()

    for i, loc in enumerate(main_locations, 1):
        search_term = clean(loc.split('(')[0])
        
        # Hinjewadi logic
        if "hinjewadi" in search_term:
            r_mask = df_rent['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
            s_mask = df_sale['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
        else:
            r_mask = df_rent['area_clean'].str.contains(search_term, na=False)
            s_mask = df_sale['area_clean'].str.contains(search_term, na=False)
        
        r_df = df_rent[r_mask]
        s_df = df_sale[s_mask]
        
        matched_rent_idx.update(r_df.index.tolist())
        matched_sale_idx.update(s_df.index.tolist())
        
        # separate duplicate counts
        r_dup = len(r_df[r_df.duplicated(subset=['owner_contact'])]) if 'owner_contact' in r_df.columns else 0
        s_dup = len(s_df[s_df.duplicated(subset=['owner_contact'])]) if 'owner_contact' in s_df.columns else 0
        
        main_rows.append({
            'Sr. No.': i, 
            'Location Name': loc,
            'No. of Rental Property Leads': len(r_df), 
            'No. of Resale Property Leads': len(s_df),
            'Total Leads': len(r_df) + len(s_df),
            'No. of duplicate data in rent': r_dup,
            'No. of duplicate data in resale': s_dup
        })

    # Extra Areas logic
    rent_extra = df_rent[~df_rent.index.isin(matched_rent_idx)]
    sale_extra = df_sale[~df_sale.index.isin(matched_sale_idx)]
    
    r_ex_sum = rent_extra.groupby('area').size().reset_index(name='Rental Leads')
    s_ex_sum = sale_extra.groupby('area').size().reset_index(name='Resale Leads')
    
    extra_df = pd.merge(r_ex_sum, s_ex_sum, on='area', how='outer').fillna(0)
    extra_df['Total Leads'] = extra_df['Rental Leads'] + extra_df['Resale Leads']
    extra_df.rename(columns={'area': 'Extra Area Name'}, inplace=True)
    
    return pd.DataFrame(main_rows), extra_df

rent_file = st.file_uploader("1. Upload Rental Leads (CSV)", type=['csv'])
sale_file = st.file_uploader("2. Upload Resale Leads (CSV)", type=['csv'])

if st.button("Generate Final Report"):
    if rent_file and sale_file:
        df_r = pd.read_csv(rent_file)
        df_s = pd.read_csv(sale_file)

        df_main, df_extra = process_data(df_r, df_s, locations)

        # Totals calculation
        total_row = pd.DataFrame([[
            'Total', '65 Locations', 
            df_main['No. of Rental Property Leads'].sum(), 
            df_main['No. of Resale Property Leads'].sum(), 
            df_main['Total Leads'].sum(), 
            df_main['No. of duplicate data in rent'].sum(), 
            df_main['No. of duplicate data in resale'].sum()
        ]], columns=df_main.columns)

        df_final = pd.concat([df_main, total_row], ignore_index=True)

        st.subheader("📊 Lead Summary with Separate Duplicates")
        st.dataframe(df_final)

        if not df_extra.empty:
            st.subheader(f"⚠️ Extra Areas Found: {len(df_extra)}")
            st.dataframe(df_extra)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Summary')
            if not df_extra.empty:
                df_extra.to_excel(writer, index=False, sheet_name='Extra Locations')
        
        st.download_button("📥 Download Final Excel Report", data=output.getvalue(), file_name="Lead_Summary_Report.xlsx")
