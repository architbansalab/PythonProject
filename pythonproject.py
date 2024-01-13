import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Automobile Sales Analysis",page_icon=":oncoming_automobile:",layout = "wide")
st.title(":oncoming_automobile: AutoMobile Sales: DashBoard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
df = pd.read_csv("autosales.csv",encoding = "ISO-8859-1")

#col1, col2 = st.columns((2))

df["ORDERDATE"]= pd.to_datetime(df["ORDERDATE"])

startDate = pd.to_datetime(df["ORDERDATE"]).min()
endDate = pd.to_datetime(df["ORDERDATE"]).max()

#with col1:
    #date1 = pd.to_datetime(st.date_input("Start Date",startDate))

#with col2:
    #date2 = pd.to_datetime(st.date_input("End Date",endDate))


#df = df[(df["ORDERDATE"] >= date1) & (df["ORDERDATE"]<=date2)].copy()

#--------------------------------------------------------

st.sidebar.header("Choose Filters: ")

date1 = pd.to_datetime(st.sidebar.date_input("Start Date",startDate))
date2 = pd.to_datetime(st.sidebar.date_input("End Date", endDate))

df = df[(df["ORDERDATE"] >= date1) & (df["ORDERDATE"]<=date2)].copy()


ProductLine = st.sidebar.multiselect("Pick The Product Line",df["PRODUCTLINE"].unique()) #use multiselect to select multiple companies

if not ProductLine:
    df2 = df.copy()
else:
    df2 = df[df["PRODUCTLINE"].isin(ProductLine )]

# For Country

Country = st.sidebar.multiselect("Pick The Country",df2["COUNTRY"].unique())

if not Country:
    df3 = df2.copy()
else:
    df3 = df2[df2["COUNTRY"].isin(Country)]
# For City 
City = st.sidebar.multiselect("Pick The City",df3["CITY"].unique())

# Filtering

if not ProductLine and not Country and not City:
    filtered_df = df
elif not Country and not City:
    filtered_df = df[df["PRODUCTLINE"].isin(ProductLine)]
elif not ProductLine and not City:
    filtered_df = df[df["COUNTRY"].isin(Country)]
elif Country and City:
    filtered_df = df3[df["COUNTRY"].isin(Country) & df3["CITY"].isin(City)]
elif ProductLine and City:
    filtered_df = df3[df["PRODUCTLINE"].isin(ProductLine) & df3["CITY"].isin(City)]
elif ProductLine and Country:
    filtered_df = df3[df["PRODUCTLINE"].isin(ProductLine) & df3["COUNTRY"].isin(Country)]
elif City:
    filtered_df = df3[df3["CITY"].isin(City)]
else:
    filtered_df = df3[df3["PRODUCTLINE"].isin(ProductLine) & df3["COUNTRY"].isin(Country) & df3["CITY"].isin(City)]


# START OF ANALYSIS 

filtered_df["month_year"] = filtered_df["ORDERDATE"].dt.to_period("M")
#st.subheader('Time Series Analysis')

#linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["SALES"].sum()).reset_index()
#fig = px.line(linechart, x = "month_year",y="SALES",labels = {"Sales":"Amount"},height=500,width = 1000,template="gridon")
#st.plotly_chart(fig,use_container_width=True)

c1, c2 = st.columns((2))

with c1:
    st.markdown("<h3 style='text-align: center; color: grey;'>Time Series Analysis</h3>", unsafe_allow_html=True)

    #st.subheader('Time Series Analysis')
    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["SALES"].sum()).reset_index()
    fig = px.line(linechart, x = "month_year",y="SALES",labels = {"Sales":"Amount"},height=300,width = 500,template="gridon")
    st.plotly_chart(fig,use_container_width=True)

with c2:
    st.markdown("<h3 style='text-align: center; color: grey;'>Distribution of Order Status</h3>", unsafe_allow_html=True)
    #st.subheader('Distribution of Order Status')

    order_status_counts = filtered_df['STATUS'].value_counts().reset_index()
    order_status_counts.columns = ['STATUS', 'COUNT']

    fig = px.pie(order_status_counts, names='STATUS', values='COUNT',
               template = "plotly_dark" ,height=300, width=500) # or color_discrete_sequence=px.colors.qualitative.Set3
    fig.update_traces(hoverinfo='label+percent+value')
    st.plotly_chart(fig)

with c1:
        
    st.subheader('Sales Relationship Analysis')

    fig2 = px.bar(filtered_df, y='COUNTRY', x='SALES', color='PRODUCTLINE', labels={'SALES': 'Sales'},
                height=300, width=450)
    # Display the grouped bar chart
    st.plotly_chart(fig2)

with c2:

    st.subheader('Relation B/W Last Order and Deal Size')

    # Create a scatter bubble chart using Plotly Express
    fig3 = px.scatter(filtered_df, x='DAYS_SINCE_LASTORDER', y='SALES', size='SALES', color='DEALSIZE',
                    labels={'DAYS_SINCE_LASTORDER': 'Days Since Last Order', 'SALES': 'Sales'},
                    size_max=30,height = 300,width=450)

    # Display the scatter bubble chart
    st.plotly_chart(fig3)

col1, col2,col3 = st.columns((3))

with col1:
    
    st.subheader('Order Analysis')

    sum_quantity_ordered = filtered_df.groupby('PRODUCTLINE')['QUANTITYORDERED'].sum().reset_index()

    # Create a radar chart using Plotly Express
    fig = px.line_polar(sum_quantity_ordered, r='QUANTITYORDERED', theta='PRODUCTLINE',
                       labels={'QUANTITYORDERED': 'Sum of Quantity Ordered'},
                        line_close=True,height = 300,width=280)

    # Display the styled radar chart
    st.plotly_chart(fig)

with col2:


    filtered_df['PROFIT_LOSS'] = (filtered_df['PRICEEACH'] - filtered_df['MSRP']) * filtered_df['QUANTITYORDERED']

    # Group by PRODUCTLINE and sum the PROFIT_LOSS for each product line
    grouped_df = filtered_df.groupby('PRODUCTLINE')['PROFIT_LOSS'].sum().reset_index()

    # Streamlit app
    st.subheader('Profit and Loss')

    # Create a bar chart using Plotly Express
    fig = px.bar(grouped_df, x='PRODUCTLINE', y='PROFIT_LOSS', labels={'PROFIT_LOSS': 'Total Profit/Loss'},height=300,width=400)

    # Display the bar chart
    st.plotly_chart(fig)

with col3:

    total_sales_per_customer = filtered_df.groupby('CUSTOMERNAME')['SALES'].sum().reset_index()
    st.subheader('Top 5 Customers')
    # Sort the DataFrame by total sales in descending order and select the top 5 customers
    top5customers = total_sales_per_customer.sort_values(by="SALES", ascending=False).head(5)

    # Create a funnel chart using Plotly Express
    fig = px.funnel(top5customers, x='SALES', y='CUSTOMERNAME',
                    labels={'SALES': 'Total Sales'},
                    color_discrete_sequence=['#001F3F'],height = 300,width=400)

    # Display the funnel chart
    st.plotly_chart(fig)
