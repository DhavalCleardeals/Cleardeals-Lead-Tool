import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool")

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

rent_file = st.file_uploader("1. Upload Rental Leads (CSV)", type=['csv'])
sale_file = st.file_uploader("2. Upload Resale Leads (CSV)", type=['csv'])

if st.button("Generate Summary Report"):
    if rent_file and sale_file:
        df_rent = pd.read_csv(rent_file)
        df_sale = pd.read_csv(sale_file)
        
        # Base Dataframe
        df_final = pd.DataFrame({'Sr. No.': range(1, len(locations) + 1), 'Location Name': locations})

        # Process Rental counts and duplicates
        rent_counts = df_rent['area'].str.strip().value_counts().reset_index()
        rent_counts.columns = ['Location Name', 'No. of Rental Property Leads']
        rent_dups = df_rent[df_rent.duplicated(subset=['owner_contact'])]['area'].str.strip().value_counts().reset_index()
        rent_dups.columns = ['Location Name', 'Duplicate data Rental Property Leads']

        # Process Sale counts and duplicates
        sale_counts = df_sale['area'].str.strip().value_counts().reset_index()
        sale_counts.columns = ['Location Name', 'No. of Resale Property Leads']
        sale_dups = df_sale[df_sale.duplicated(subset=['owner_contact'])]['area'].str.strip().value_counts().reset_index()
        sale_dups.columns = ['Location Name', 'Duplicate Data Resale Property Leads']

        # Merge all into final table
        df_final = df_final.merge(rent_counts, on='Location Name', how='left')
        df_final = df_final.merge(sale_counts, on='Location Name', how='left')
        df_final = df_final.merge(rent_dups, on='Location Name', how='left')
        df_final = df_final.merge(sale_dups, on='Location Name', how='left').fillna(0)

        # Total Leads row wise
        df_final['Total Leads'] = df_final['No. of Rental Property Leads'] + df_final['No. of Resale Property Leads']
        
        # Column Ordering as per your Excel
        cols = ['Sr. No.', 'Location Name', 'No. of Rental Property Leads', 'No. of Resale Property Leads', 'Total Leads', 'Duplicate data Rental Property Leads', 'Duplicate Data Resale Property Leads']
        df_final = df_final[cols]

        # Calculation for Row 66: Total Sums
        sums = df_final.sum(numeric_only=True)
        total_row = pd.DataFrame([[
            'Total', '65 Locations', sums['No. of Rental Property Leads'], sums['No. of Resale Property Leads'], 
            sums['Total Leads'], sums['Duplicate data Rental Property Leads'], sums['Duplicate Data Resale Property Leads']
        ]], columns=cols)

        # Calculation for Row 67: Total Locations Count (where leads > 0)
        loc_rent = (df_final['No. of Rental Property Leads'] > 0).sum()
        loc_sale = (df_final['No. of Resale Property Leads'] > 0).sum()
        loc_row = pd.DataFrame([[
            None, None, f"Total Location {loc_rent}", f"Total Location {loc_sale}", None, None, None
        ]], columns=cols)

        # Concatenate rows to display
        df_display = pd.concat([df_final, total_row, loc_row], ignore_index=True)

        st.success("✅ Report Taiyar Che!")
        st.dataframe(df_display)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_display.to_excel(writer, index=False, sheet_name='Summary')
        st.download_button("📥 Download Final Excel Report", data=output.getvalue(), file_name="Lead_Summary_Final.xlsx")
