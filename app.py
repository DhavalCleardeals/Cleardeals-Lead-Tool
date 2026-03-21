import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Full Extra Details)")

locations = [
    "Alandi", "Aundh", "Bakori", "Balewadi", "Baner", "Bavdhan", "Bhekraiwadi", "Bhosari", "Bibewad", "Blue Ridge",
    "Camp", "Chandan Nagar", "Chinchwad", "Dapodi", "Dhayri", "Dhanori", "Dighi", "Dudulgaon", "Fursungi", "Gahunje",
    "Ghorpadi", "Hadapsar", "Hinjewadi (All Phases)", "Kalyani Nagar", "Karvenagar", "Kasarwadi", "Katraj", "Keshav Nagar",
    "Khadakwasla", "Kharadi", "Kiwale", "Kondhwa", "Kothrud", "Loni Kalbhor", "Lohegaon", "Lonavala", "Magarpatta",
    "Mahalunge", "Mamurdi", "Manjari", "Moshi", "Mundhwa", "Narayangaon", "Nigdi", "btp", "Pashan", "Phursungi",
    "Pimple Gurav", "Pimple Nilakh", "Pimple Saudagar", "Pimpri", "Pisoli", "Punawale", "Ravet", "Sangvi", "Sasane Nagar",
    "Shikrapur", "Tathawade", "Tingre Nagar", "Undri", "Viman Nagar", "Vishrantwadi", "Wadgaon Sheri", "Wagholi", "Wakad", "Warje"
]

def clean(text):
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

def process_data(df_rent, df_sale, main_locations):
    # Prepare DataFrames
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
            'Rental Leads': len(r_df), 'Resale Leads': len(s_df),
            'Total Leads': len(r_df) + len(s_df),
            'Rental Dup
