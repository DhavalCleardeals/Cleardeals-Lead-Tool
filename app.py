import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Cleardeals Automation", layout="wide")
st.title("🏠 Cleardeals Lead Summary Tool")

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
        df_final = pd.DataFrame({'Sr. No.': range(1, len(locations) + 1), 'Location Name': locations})

        rent_counts = df_rent['area'].str.strip().value_counts().reset_index()
        rent_counts.columns = ['Location Name', 'Rental Leads']
        sale_counts = df_sale['area'].str.strip().value_counts().reset_index()
        sale_counts.columns = ['Location Name', 'Resale Leads']

        df_final = df_final.merge(rent_counts, on='Location Name', how='left')
        df_final = df_final.merge(sale_counts, on='Location Name', how='left').fillna(0)
        df_final['Total Leads'] = df_final['Rental Leads'] + df_final['Resale Leads']

        total_row = pd.DataFrame([['Total', '65 Locations', df_final['Rental Leads'].sum(), df_final['Resale Leads'].sum(), df_final['Total Leads'].sum()]], columns=df_final.columns)
        df_display = pd.concat([df_final, total_row], ignore_index=True)

        st.success("✅ Report Taiyar Hai!")
        st.dataframe(df_display)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_display.to_excel(writer, index=False)
        st.download_button("📥 Download Excel File", data=output.getvalue(), file_name="Summary_Report.xlsx")
