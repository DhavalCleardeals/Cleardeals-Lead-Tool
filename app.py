import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Smart Matching)")

# 65 Standard Locations List
locations = [
    "Alandi", "Aundh", "Bakori", "Balewadi", "Baner", "Bavdhan", "Bhekraiwadi", "Bhosari", "Bibewad", "Blue Ridge",
    "Camp", "Chandan Nagar", "Chinchwad", "Dapodi", "Dhayri", "Dhanori", "Dighi", "Dudulgaon", "Fursungi", "Gahunje",
    "Ghorpadi", "Hadapsar", "Hinjewadi (All Phases)", "Kalyani Nagar", "Karvenagar", "Kasarwadi", "Katraj", "Keshav Nagar",
    "Khadakwasla", "Kharadi", "Kiwale", "Kondhwa", "Kothrud", "Loni Kalbhor", "Lohegaon", "Lonavala", "Magarpatta",
    "Mahalunge", "Mamurdi", "Manjari", "Moshi", "Mundhwa", "Narayangaon", "Nigdi", "btp", "Pashan", "Phursungi",
    "Pimple Gurav", "Pimple Nilakh", "Pimple Saudagar", "Pimpri", "Pisoli", "Punawale", "Ravet", "Sangvi", "Sasane Nagar",
    "Shikrapur", "Tathawade", "Tingre Nagar", "Undri", "Viman Nagar", "Vishrantwadi", "Wadgaon Sheri", "Wagholi", "Wakad", "Warje"
]

def get_counts(df, location_list):
    """Smart matching logic to handle spelling variations"""
    counts = {}
    dups = {}
    
    # Pre-clean the area column (make it lowercase for matching)
    df['area_clean'] = df['area'].astype(str).str.lower().str.strip()
    
    for loc in location_list:
        # Search criteria based on location name
        search_term = loc.split('(')[0].strip().lower() # Takes 'Hinjewadi' from 'Hinjewadi (All Phases)'
        
        if "hinjewadi" in search_term:
            # Special case for Hinjewadi/Hinjawadi
            match_condition = df['area_clean'].str.contains('hinjewadi|hinjawadi', case=False, na=False)
        else:
            match_condition = df['area_clean'].str.contains(search_term, case=False, na=False)
            
        temp_df = df[match_condition]
        counts[loc] = len(temp_df)
        dups[loc] = len(temp_df[temp_df.duplicated(subset=['owner_contact'])])
        
    return counts, dups

rent_file = st.file_uploader("1. Upload Rental Leads (CSV)", type=['csv'])
sale_file = st.file_uploader("2. Upload Resale Leads (CSV)", type=['csv'])

if st.button("Generate Summary Report"):
    if rent_file and sale_file:
        try:
            df_rent = pd.read_csv(rent_file)
            df_sale = pd.read_csv(sale_file)
            
            # Use Smart Matching to get counts
            rent_counts, rent_dups = get_counts(df_rent, locations)
            sale_counts, sale_dups = get_counts(df_sale, locations)

            # Build final table
            rows = []
            for i, loc in enumerate(locations, 1):
                r_cnt = rent_counts.get(loc, 0)
                s_cnt = sale_counts.get(loc, 0)
                rows.append({
                    'Sr. No.': i,
                    'Location Name': loc,
                    'No. of Rental Property Leads': r_cnt,
                    'No. of Resale Property Leads': s_cnt,
                    'Total Leads': r_cnt + s_cnt,
                    'Duplicate data Rental Property Leads': rent_dups.get(loc, 0),
                    'Duplicate Data Resale Property Leads': sale_dups.get(loc, 0)
                })

            df_final = pd.DataFrame(rows)

            # Footer Rows (Total Sum)
            sums = df_final.sum(numeric_only=True)
            total_row = pd.DataFrame([[
                'Total', '65 Locations', sums['No. of Rental Property Leads'], sums['No. of Resale Property Leads'], 
                sums['Total Leads'], sums['Duplicate data Rental Property Leads'], sums['Duplicate Data Resale Property Leads']
            ]], columns=df_final.columns)

            # Footer Rows (Total Locations Count)
            loc_rent = (df_final['No. of Rental Property Leads'] > 0).sum()
            loc_sale = (df_final['No. of Resale Property Leads'] > 0).sum()
            loc_row = pd.DataFrame([[
                None, None, f"Total Location {loc_rent}", f"Total Location {loc_sale}", None, None, None
            ]], columns=df_final.columns)

            df_display = pd.concat([df_final, total_row, loc_row], ignore_index=True)

            st.success("✅ Report Updated with Smart Spelling Matching!")
            st.dataframe(df_display)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Summary')
            st.download_button("📥 Download Corrected Excel Report", data=output.getvalue(), file_name="Lead_Summary_Corrected.xlsx")
        except Exception as e:
            st.error(f"Error: {e}. Please ensure CSV columns are named 'area' and 'owner_contact'.")
