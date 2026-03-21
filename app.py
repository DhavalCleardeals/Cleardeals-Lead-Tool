import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Final Extra Area Logic)")

# Your Updated 65 Locations List
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
    df_rent['area_clean'] = df_rent['area'].apply(clean)
    df_sale['area_clean'] = df_sale['area'].apply(clean)
    
    main_rows = []
    matched_rent_indices = []
    matched_sale_indices = []

    for i, loc in enumerate(main_locations, 1):
        clean_loc = clean(loc.split('(')[0])
        
        # Smart Matching Logic
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
            'Duplicate data Rental Property Leads': len(r_df[r_df.duplicated(subset=['owner_contact'])]),
            'Duplicate Data Resale Property Leads': len(s_df[s_df.duplicated(subset=['owner_contact'])])
        })

    # Extra Areas logic
    rent_extra = df_rent[~df_rent.index.isin(matched_rent_indices)].copy()
    sale_extra = df_sale[~df_sale.index.isin(matched_sale_indices)].copy()
    
    r_extra_sum = rent_extra.groupby('area').size().reset_index(name='Rental Leads')
    s_extra_sum = sale_extra.groupby('area').size().reset_index(name='Resale Leads')
    
    extra_combined = pd.merge(r_extra_sum, s_extra_sum, on='area', how='outer').fillna(0)
    extra_combined['Total Leads'] = extra_combined['Rental Leads'] +
