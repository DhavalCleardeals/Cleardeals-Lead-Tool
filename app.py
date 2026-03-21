import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Fixed Error)")

# Your 65 Locations List
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
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

def process_data(df_rent, df_sale, main_locations):
    # Ensure area exists
    for df in [df_rent, df_sale]:
        if 'area' not in df.columns:
            st.error("Error: CSV file must have an 'area' column.")
            return None, None
            
    df_rent['area_clean'] = df_rent['area'].apply(clean)
    df_sale['area_clean'] = df_sale['area'].apply(clean)
    
    main_rows = []
    matched_rent_indices = []
    matched_sale_indices = []

    for i, loc in enumerate(main_locations, 1):
        clean_loc = clean(loc.split('(')[0])
        
        # Matching logic
        if "hinjewadi" in clean_loc:
            r_mask = df_rent['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
            s_mask = df_sale['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
        else:
            r_mask = df_rent['area_clean'].str.contains(clean_loc, na=False)
            s_mask = df_sale['area_clean'].str.contains(clean_loc, na=False)
        
        r_df = df_rent[r_mask]
        s_df = df_sale[s_mask]
        
        matched_rent_indices.extend(r_df.index.tolist())
        matched_sale_indices.extend(s_df.index.tolist())
        
        main_rows.append({
            'Sr. No.': i, 'Location Name': loc,
            'No. of Rental Property Leads': len(r_df), 
            'No. of Resale Property Leads': len(s_df),
            'Total Leads': len(r_df) + len(s_df),
            'Duplicate data Rental Property Leads': len(r_df[r_df.duplicated(subset=['owner_contact'])]) if 'owner_contact' in r_df.columns else 0,
            'Duplicate Data Resale Property Leads': len(s_df[s_df.duplicated(subset=['owner_contact'])]) if 'owner_contact' in s_df.columns else 0
        })

    # Extra Areas logic
    rent_extra = df_rent[~df_rent.index.isin(matched_rent_indices)].copy()
    sale_extra = df_sale[~df_sale.index.isin(matched_sale_indices)].copy()
    
    r_extra_sum = rent_extra.groupby('area').size().reset_index(name='Rental Leads')
    s_extra_sum = sale_extra.groupby('area').size().reset_index(name='Resale Leads')
    
    extra_combined = pd.merge(r_extra_sum, s_extra_sum, on='area', how='outer').fillna(0)
    extra_combined['Total Leads'] = extra_combined['Rental Leads'] + extra_combined['Resale Leads']
    extra_combined.rename(columns={'area': 'Extra Area Name'}, inplace=True)
    
    return pd.DataFrame(main_rows), extra_combined

rent_file = st.file_uploader("1. Upload Rental CSV", type=['csv'])
sale_file = st.file_uploader("2. Upload Resale CSV", type=['csv'])

if st.button("Generate Complete Report"):
    if rent_file and sale_file:
        df_r = pd.read_csv(rent_file)
        df_s = pd.read_csv(sale_file)

        df_main, df_extra = process_data(df_r, df_s, locations)

        if df_main is not None:
            # Totals logic
            total_rent = df_main['No. of Rental Property Leads'].sum()
            total_sale = df_main['No. of Resale Property Leads'].sum()
            total_all = df_main['Total Leads'].sum()
            total_rent_dup = df_main['Duplicate data Rental Property Leads'].sum()
            total_sale_dup = df_main['Duplicate Data Resale Property Leads'].sum()

            total_row = pd.DataFrame([[
                'Total', '65 Locations', total_rent, total_sale, total_all, total_rent_dup, total_sale_dup
            ]], columns=df_main.columns)

            df_final_main = pd.concat([df_main, total_row], ignore_index=True)

            st.subheader("📊 Main 65 Locations Summary")
            st.dataframe(df_final_main)

            if not df_extra.empty:
                st.subheader(f"⚠️ Extra Locations Found: {len(df_extra)}")
                st.dataframe(df_extra)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final_main.to_excel(writer, index=False, sheet_name='Summary')
                    
                    extra_title = pd.DataFrame([['', 'EXTRA LOCATIONS LIST BELOW', '', '', '']])
                    extra_title.to_excel(writer, index=False, header=False, sheet_name='Summary', startrow=len(df_final_main)+2)
                    
                    df_extra.to_excel(writer, index=False, sheet_name='Summary', startrow=len(df_final_main)+4)
                
                st.download_button("📥 Download Final Report", data=output.getvalue(), file_name="Lead_Summary_Report.xlsx")
            else:
                st.success("બધી લોકેશન મેચ થઈ ગઈ છે!")
