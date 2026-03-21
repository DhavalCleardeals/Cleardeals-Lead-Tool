import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool (Final Fix)")

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

def process_data(df, location_list):
    df['area_clean'] = df['area'].astype(str).str.lower().str.strip()
    results = []
    matched_indices = set()

    for i, loc in enumerate(location_list, 1):
        search_term = loc.split('(')[0].strip().lower()
        if "hinjewadi" in search_term:
            mask = df['area_clean'].str.contains('hinjewadi|hinjawadi', na=False)
        else:
            mask = df['area_clean'].str.contains(search_term, na=False)
        
        matched_df = df[mask]
        matched_indices.update(matched_df.index)
        
        results.append({
            'loc': loc,
            'count': len(matched_df),
            'dups': len(matched_df[matched_df.duplicated(subset=['owner_contact'])])
        })
    
    # Check for unmatched areas
    unmatched_df = df[~df.index.isin(matched_indices)]
    return results, unmatched_df

rent_file = st.file_uploader("1. Upload Rental CSV", type=['csv'])
sale_file = st.file_uploader("2. Upload Resale CSV", type=['csv'])

if st.button("Generate Final Report"):
    if rent_file and sale_file:
        df_rent = pd.read_csv(rent_file)
        df_sale = pd.read_csv(sale_file)
        
        rent_res, rent_unmatched = process_data(df_rent, locations)
        sale_res, sale_unmatched = process_data(df_sale, locations)

        final_rows = []
        for i, loc in enumerate(locations):
            final_rows.append({
                'Sr. No.': i+1,
                'Location Name': loc,
                'No. of Rental Property Leads': rent_res[i]['count'],
                'No. of Resale Property Leads': sale_res[i]['count'],
                'Total Leads': rent_res[i]['count'] + sale_res[i]['count'],
                'Duplicate data Rental Property Leads': rent_res[i]['dups'],
                'Duplicate Data Resale Property Leads': sale_res[i]['dups']
            })

        df_final = pd.DataFrame(final_rows)
        
        # Totals
        sums = df_final.sum(numeric_only=True)
        total_row = pd.DataFrame([['Total', '65 Locations', sums[0], sums[1], sums[2], sums[3], sums[4]]], columns=df_final.columns)
        df_display = pd.concat([df_final, total_row], ignore_index=True)

        st.success("✅ Report Taiyar!")
        st.dataframe(df_display)

        # Show Unmatched Data
        if not sale_unmatched.empty:
            st.warning("⚠️ Ye areas Resale file mein mile par hamari list mein nahi the:")
            st.write(sale_unmatched['area'].unique())

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_display.to_excel(writer, index=False, sheet_name='Summary')
        st.download_button("📥 Download Excel", data=output.getvalue(), file_name="Final_Report.xlsx")
