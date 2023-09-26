import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fuzzywuzzy import fuzz, process

st.set_page_config(page_title='Indian startup analysis')
df = pd.read_csv('startup_cleaned_v5.csv')
df.drop(columns='Unnamed: 0', inplace=True)

# converting amount to crores
df['amount'] = df['amount'] / 10000000

# changing flipkart.com to flipkart
df.loc[2648,'startup_name'] = 'flipkart'

user_choice= st.sidebar.selectbox('show analysis with respect to', ['investor','startup','general analysis'])
if user_choice == 'investor':
    investors_list = sorted(df['investor'].fillna('missing').unique().tolist())

    selected_investor = st.sidebar.selectbox('select an investor', investors_list)
    analysis_button= st.sidebar.button('show analysis')

    if analysis_button:
        # show recent investments
        def display_recent_investments(df, investor_name):
            temp = df[df['investor'].fillna('missing').str.contains(investor_name)].sort_values(by='date',
                                                                                                ascending=False)
            return temp

        st.header('Recent investments')
        st.dataframe(display_recent_investments(df, selected_investor))

        # display biggest investment

        def display_biggest_investment(df, investor_name):
            temp = (df[df['investor']
                    .fillna('missing')
                    .str.contains(investor_name)]
                    .sort_values(by='amount', ascending=False)
                    .head(1))

            return temp


        st.header('Biggest investment')
        biggest_investment = display_biggest_investment(df,selected_investor)
        st.dataframe(biggest_investment)

        # display the industry vertical they generally invest in
        def display_generally_invests_in(df, investor_name):
            temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
            result = (temp
                      .groupby('industry_vertical')['date'].count()
                      .sort_values(ascending=False)
                      .head(1)
                      .index[0]
                      .title())
            return result


        result = display_generally_invests_in(df, selected_investor)
        st.title('Generally invest(s) in: ')
        st.subheader(result)


        # display pie chart of top  sectors the investor invests in
        def display_sector_pie(df, investor_name):
            temp = df[df['investor'].fillna('missing').str.contains(investor_name)]

            data = temp.groupby('industry_vertical')['date'].count().sort_values(ascending=False).head(7).reset_index()
            data.rename(columns={'date': 'num_investments'}, inplace=True)

            # Plot the pie chart using Plotly Express
            fig = px.pie(data, names='industry_vertical', values='num_investments',
                         title='Top Industry Verticals they invest in',
                         hover_data=['industry_vertical'])

            return fig
        result = display_sector_pie(df, selected_investor)
        st.plotly_chart(result)


        # display pie chart of top investment types of the selected investor
        def display_top_investment_types(df, investor_name):
            temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
            data = temp.groupby('investment_type')['date'].count().reset_index()
            data.rename(columns={'date': 'num_investments'}, inplace=True)

            fig = px.pie(data, names='investment_type', values='num_investments', title='Investment round breakdown',
                         hover_data=['investment_type'])

            return fig

        result = display_top_investment_types(df, selected_investor)
        st.plotly_chart(result)


        # display pie chart of top cities the investor invests in
        def display_top_cities(df, investor_name):
            temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
            data = temp.groupby('city')['date'].count().sort_values(ascending=False).head(7).reset_index()
            data.rename(columns={'date': 'num_investments'}, inplace=True)

            fig = px.pie(data, names='city', values='num_investments',
                         title='Top locations the investor(s) have made investments in ',
                         hover_data=['city'])

            return fig


        result = display_top_cities(df, selected_investor)
        st.plotly_chart(result)


        # display YoY investments
        col1, col2= st.columns(2)

        with col1:
            def display_yoy_investment(df, investor_name):
                temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
                temp['date'] = pd.to_datetime(temp['date'])
                temp['year'] = temp['date'].dt.year

                required_df = temp.groupby('year')['amount'].sum()
                fig1 = px.line(required_df, x=required_df.index, y=required_df.values,
                               title=' Trend of investment amount over years')
                fig1.update_xaxes(tickvals=required_df.index)
                fig1.update_yaxes(title='amount (in crores INR)')
                fig1.update_layout(
                    width=600,  # Specify the width in pixels
                    height=400  # Specify the height in pixels
                )

                return fig1
            result1 = display_yoy_investment(df, selected_investor)
            st.plotly_chart(result1)


        with col2:
            def display_yoy_num_investments(df, investor_name):
                temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
                temp['date'] = pd.to_datetime(temp['date'])
                temp['year'] = temp['date'].dt.year

                # number of investments over years
                new_df = temp.groupby('year')['date'].count()
                fig2 = px.line(new_df, x=new_df.index, y=new_df.values,
                               title='Trend of number of investments over years')
                fig2.update_xaxes(tickvals=new_df.index)
                fig2.update_yaxes(title='number of investments')
                fig2.update_layout(
                    width=600,  # Specify the width in pixels
                    height=400  # Specify the height in pixels
                )

                return fig2

            result2 = display_yoy_num_investments(df, selected_investor)
            st.plotly_chart(result2)


        # display similar startups based on teh selected startup's name
        def find_similar_startup_names(query, df, threshold=60):
            # Create a list to store similar startup names
            similar_names = []

            # Iterate through startup names in the DataFrame
            for startup_name in df['startup_name']:
                similarity = fuzz.ratio(query.lower(), startup_name.lower())

                # If the similarity ratio is above the threshold, consider it a match
                if similarity >= threshold:
                    similar_names.append((startup_name, similarity))

            # Sort the results by similarity score (optional)
            similar_names.sort(key=lambda x: x[1], reverse=True)

            return similar_names

        query = selected_investor
        similar_startup_names = find_similar_startup_names(query, df)

        # Print the results
        similar_startups = []
        for name, similarity in similar_startup_names:
            similar_startups.append(name)

        st.dataframe(similar_startups, hide_index=True)


df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year


# 2. General analysis
if user_choice == 'general analysis':

    button = st.sidebar.button('show analysis')

    if button:
        # display cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Number of startups', str(df['startup_name'].nunique()))

        with col2:
            st.metric('Total amount invested (in crores INR)', str(round(df['amount'].sum(),2)))


        with col3:
            st.metric('Avg investment amount (crores INR)', str(round(df['amount'].mean(),2)))


        # display MoM chart of invesments over years
        st.title('Month on month trends of number of startups that get investments')
        temp = df.groupby(['year', 'month'])['startup_name'].count().reset_index()
        temp.rename(columns={'startup_name': 'count'}, inplace=True)
        temp['x-axis'] = temp['month'].astype('str') + "-" + temp['year'].astype('str')
        temp.rename(columns={'x-axis': 'month-year'}, inplace=True)

        fig = px.line(data_frame=temp, x='month-year', y='count')
        fig.update_layout(height=500, width=1000)
        fig.update_xaxes(tickangle=270)
        st.plotly_chart(fig)


        # display MoM trends based on investment amount
        st.title('Month on month trends of total investments in startups')
        temp = df.groupby(['year', 'month'])['amount'].sum().reset_index()
        temp['month-year'] = temp['month'].astype('str') + "-" + temp['year'].astype('str')

        fig = px.line(data_frame=temp, x='month-year', y='amount')
        fig.update_layout(height=500, width=1000)
        fig.update_xaxes(tickangle=270)

        st.plotly_chart(fig)


        # display top sectors: a) based on number of startups in the sector
        # b) based on the amount of investment in the sector

        col1, col2 = st.columns([12,12])

        with col1:
            st.title('Top sectors in terms of number of startups')
            temp = df.groupby('industry_vertical')['startup_name'].count().sort_values(ascending=False).head(10)
            fig = px.pie(data_frame=temp, names=temp.index, values=temp.values)
            fig.update_layout(height=450, width=450, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.write('##')

        with col2:
            st.title('Top sectors in terms of investment amount')
            temp = df.groupby('industry_vertical')['amount'].sum().round().sort_values(ascending=False).head(10)
            fig = px.pie(data_frame=temp, names=temp.index, values=temp.values)
            fig.update_layout(height=450, width=450, showlegend=False)

            st.plotly_chart(fig, use_container_width=True)


        # funding type vs investment amount
        st.title('Investment type vs. avg investment amount')
        st.write('The average investment amount has been converted to log of the amount for easier comparison')
        temp = df.groupby('investment_type')['amount'].mean().sort_values(ascending=False)
        fig = px.bar(data_frame=temp, x=temp.index, y=np.log(temp.values))
        fig.update_xaxes(tickangle=270)
        fig.update_yaxes(title_text='log (invesment_amount in crores INR)')
        fig.update_layout(height=500, width=1000)

        st.plotly_chart(fig)


        # CITYWISE FUNDING
        col1, col2= st.columns(2)
        with col1:
            # show top 10 cities by investment amount
            st.header('Top 10 cities by investment amount')
            temp = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.pie(data_frame=temp, names='city', values='amount')
            fig.update_layout(showlegend=False)

            st.plotly_chart(fig)

        with col2:
            # top 10 cities by number of investments
            st.header('Top 10 cities by number of investments')
            temp = df.groupby('city')['startup_name'].count().sort_values(ascending=False).head(10)
            fig = px.pie(names=temp.index, values=temp.values)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig)

        # which sector gets highest investment on average in each city?
        st.header('which sector gets highest investment on average in each city?')
        temp = df.groupby(['city', 'industry_vertical'])['amount'].agg('mean').reset_index()
        required_idx = temp.groupby('city')['amount'].idxmax()

        required_idx = required_idx.dropna()  # drop na values
        # fetch the rows with the required_idx
        result = temp.loc[required_idx].reset_index().drop(columns='index').T
        st.dataframe(result)

        # TOP STARTUPS
        col1, col2 = st.columns(2)

        with col1:
            # top 10 startups in terms of funding they have received till now
            st.title('Top 10 startups who scored the highest investment')
            result_df = df.groupby('startup_name')['amount'].sum().round().sort_values(ascending=False).head(10).reset_index()
            st.dataframe(result_df)

        with col2:
            # top startup each year
            st.title('Startup with highest investment each year')
            temp = df.groupby(['year', 'startup_name'])['amount'].sum().round().reset_index()
            required_idx = temp.groupby('year')['amount'].idxmax()
            result_df = temp.loc[required_idx]
            st.dataframe(result_df)


        # TOP INVESTORS
        col1, col2= st.columns(2)

        with col1:
            # top 10 investors in terms of number of investments
            st.title('Top 10 investors by investment count')
            result = df.groupby('investor')['startup_name'].count().sort_values(ascending=False)[1:].head(10)
            result.rename({'startup_name':'investment_count'}, inplace=True)
            st.dataframe(result)

        with col2:
            # top 10 investors in terms of total investment till now
            st.title('Top 10 investors by total investment amount')
            result = df.groupby('investor')['amount'].sum().round().sort_values(ascending=False).head(10)
            st.dataframe(result)



#3. Startup
if user_choice=='startup':
    selected_startup = st.sidebar.selectbox('select a startup: ', sorted(df['startup_name'].unique().tolist()))
    button = st.sidebar.button('Show analysis')

    if button:
        #display name
        st.header(f'Name : {selected_startup.title()}')

        # display vertical
        vertical = df[df['startup_name'] == selected_startup]['industry_vertical'].values[0]
        st.header(f'Industry vertical : {vertical}')

        # display sub-vertical
        subvertical = df[df['startup_name'] == selected_startup]['subvertical'].values[0]
        st.header(f'Industry subvertical : {subvertical}')

        # displaying investments
        temp = df[df['startup_name'] == selected_startup].drop(columns=['year','month'])
        st.dataframe(temp)