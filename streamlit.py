import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from streamlit_option_menu import option_menu

def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )

connection = connect_to_mysql()

query = """
SELECT 
    Bus_name, Route_Link, Route, Bus_Type, Departing_Time, Duration, 
    Reaching_Time, ROUND(Star_Rating, 1) AS Star_Rating, 
    ROUND(Price, 2) AS Price, Seat_Available, Departure, Arrival 
FROM RedBus.Red_Bus_Cleansed_Data
"""
cursor = connection.cursor(buffered=True)
cursor.execute(query)
data = cursor.fetchall()
cursor.close()
connection.close()

columns = [
    "Bus_name", "Route_Link", "Route", "Bus_Type", "Departing_Time", "Duration", 
    "Reaching_Time", "Star_Rating", "Price", "Seat_Available", "Departure", "Arrival"
]
Bus_Data = pd.DataFrame(data, columns=columns)

Bus_Data["Departing_Time"] = pd.to_datetime(Bus_Data["Departing_Time"], errors='coerce')
Bus_Data["Reaching_Time"] = pd.to_datetime(Bus_Data["Reaching_Time"], errors='coerce')

Bus_Data = Bus_Data.dropna(subset=["Departing_Time", "Reaching_Time"])

st.set_page_config(
    page_title="RED BUS",
    page_icon=":guardsman:",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Bus_Analysis"])

if select == "Home":
    st.title("RedBus Data Analysis")
    st.image(r"C:/Users/BARATH KANNAN/OneDrive/Desktop/red.png", caption="WELCOME TO DATA INSIGHT", use_column_width=True)

if select == "Bus_Analysis":
    route_selected = st.sidebar.selectbox("Select Route", Bus_Data["Route"].unique())
    filtered_data = Bus_Data[Bus_Data["Route"] == route_selected]
    
    if not filtered_data.empty:
        st.sidebar.write(f"Route Link: {filtered_data['Route_Link'].iloc[0]}")
        st.sidebar.write(f"Average Price: {round(filtered_data['Price'].mean(), 2)}")

        star_rating_filter = st.sidebar.slider("Filter by Star Rating", 0.0, 5.0, (0.0, 5.0), 0.1)
        filtered_data = filtered_data[(filtered_data["Star_Rating"] >= star_rating_filter[0]) & (filtered_data["Star_Rating"] <= star_rating_filter[1])]
        
        price_range = st.sidebar.slider("Filter by Price Range", float(filtered_data["Price"].min()), float(filtered_data["Price"].max()), (float(filtered_data["Price"].min()), float(filtered_data["Price"].max())), 0.1)
        filtered_data = filtered_data[(filtered_data["Price"] >= price_range[0]) & (filtered_data["Price"] <= price_range[1])]

        min_departing_time = filtered_data["Departing_Time"].min().time()
        max_departing_time = filtered_data["Departing_Time"].max().time()
        min_reaching_time = filtered_data["Reaching_Time"].min().time()
        max_reaching_time = filtered_data["Reaching_Time"].max().time()

        departing_time_range = st.sidebar.slider(
            "Filter by Departing Time",
            min_value=min_departing_time,
            max_value=max_departing_time,
            value=(min_departing_time, max_departing_time),
            format="HH:mm"
        )
        reaching_time_range = st.sidebar.slider(
            "Filter by Reaching Time",
            min_value=min_reaching_time,
            max_value=max_reaching_time,
            value=(min_reaching_time, max_reaching_time),
            format="HH:mm"
        )

        filtered_data = filtered_data[
            (filtered_data["Departing_Time"].dt.time >= departing_time_range[0]) &
            (filtered_data["Departing_Time"].dt.time <= departing_time_range[1]) &
            (filtered_data["Reaching_Time"].dt.time >= reaching_time_range[0]) &
            (filtered_data["Reaching_Time"].dt.time <= reaching_time_range[1])
        ]
     
        tab1, tab2 = st.tabs(["Bus Details", "Chart Analysis"])

        with tab1:
            st.write(f"Buses for Route: {route_selected}")

            if not filtered_data.empty:
                st.write("Buses Details:")
                st.table(filtered_data.reset_index(drop=True))
            else:
                st.write("No buses available for the selected route, rating filter, departure, and arrival.")

        with tab2:
            st.write("Visual Analysis")
            
            top_10_seat_availability = filtered_data.nlargest(10, 'Seat_Available')
            top_10_seat_avail_chart = px.bar(top_10_seat_availability, x='Bus_name', y='Seat_Available', color='Bus_name', title='Top 10 Seat Availability Across Buses')
            st.plotly_chart(top_10_seat_avail_chart)
            
            price_histogram = px.histogram(filtered_data, x='Price', nbins=50, title='Distribution of Prices')
            st.plotly_chart(price_histogram)
            
            star_rating_hist = px.histogram(filtered_data, x='Star_Rating', nbins=10, title='Distribution of Star Ratings')
            st.plotly_chart(star_rating_hist)
            
            bus_type_pie = px.pie(Bus_Data, names='Bus_Type', title='Distribution of Bus Types')
            st.plotly_chart(bus_type_pie)
            
            price_vs_rating_scatter = px.scatter(filtered_data, x='Star_Rating', y='Price', color='Bus_name', title='Price vs. Star Rating')
            st.plotly_chart(price_vs_rating_scatter)
            
            time_analysis = px.scatter(filtered_data, x='Departing_Time', y='Reaching_Time', color='Bus_name', title='Departure vs. Arrival Time')
            st.plotly_chart(time_analysis)
        
    else:
        st.write("No data available for the selected route.")
    