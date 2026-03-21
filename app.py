import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (With Extra Areas)")

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

def process_with_extra(df, main_locations):
    df['area_clean'] = df['area'].apply(clean)
    main_counts = {loc: 0 for loc in main_locations}
    main_dups = {loc: 0 for loc in main_locations}
    matched_indices = []

    # Match main locations
    for loc in main_locations:
        clean_loc = clean(loc.split('(')[0])
        mask = df['area_clean'].str.contains(clean_loc, na=False)
        if clean_loc == "hinjewadi":
            mask = df['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
        
        matched_df = df[mask]
        main_counts[loc] = len(matched_df)
        main_dups[loc] = len(matched_df[matched_df.duplicated(subset=['owner_contact'])])
        matched_indices.extend(matched_df.index.tolist())

    # Identify Extra Locations
    extra_df = df[~df.index.isin(matched_indices)].copy()
    extra_summary = extra_df.groupby('area').agg(
        Leads=('area', 'count'),
        Duplicates=('owner_contact', lambda x: x.duplicated().sum())
    ).reset_index()
    
    return main_counts, main_dups, extra_summary

rent_file = st.file_uploader("1. Upload Rental CSV", type=['csv'])
sale_file = st.file_uploader("2. Upload Resale CSV", type=['csv'])

if st.button("Generate Report with Extra Areas"):
    if rent_file and sale_file:
        df_rent = pd.read_csv(rent_file)
        df_sale = pd.read_csv(sale_file)

        r_main, r_dup, r_extra = process_with_extra(df_rent, locations)
        s_main, s_dup, s_extra = process_with_extra(df_sale, locations)

        # 1. Main Table
        rows = []
        for i, loc in enumerate(locations, 1):
            rows.append({
                'Sr. No.': i, 'Location Name': loc,
                'Rental Leads': r_main[loc], 'Resale Leads': s_main[loc],
                'Total': r_main[loc] + s_main[loc],
                'Rental Dup': r_dup[loc], 'Resale Dup': s_dup[loc]
            })
        df_final = pd.DataFrame(rows)

        # 2. Totals
        sums = df_final.sum(numeric_only=True)
        total_row = pd.DataFrame([['Total', '65 Locations', sums[1], sums[2], sums[3], sums[4], sums[5]]], columns=df_final.columns)
        
        st.subheader("📊 Main 65 Locations Summary")
        st.dataframe(pd.concat([df_final, total_row], ignore_index=True))

        # 3. Extra Locations Table
        st.subheader("⚠️ Extra Locations Found (Not in List)")
        all_extra = pd.concat([r_extra.assign(Type='Rental'), s_extra.assign(Type='Resale')])
        if not all_extra.empty:
            st.dataframe(all_extra)
            st.info(f"Total Extra Areas Found: {len(all_extra['area'].unique())}")
        else:
            st.success("No extra locations found!")

        # Excel Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.concat([df_final, total_row], ignore_index=True).to_excel(writer, index=False, sheet_name='Main_Summary')
            all_extra.to_excel(writer, index=False, sheet_name='Extra_Locations')
        st.download_button("📥 Download Excel (Includes Extra Areas)", data=output.getvalue(), file_name="Cleardeals_Final_Report.xlsx")
