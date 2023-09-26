
import plotly.express as px
import pandas as pd
from fuzzywuzzy import fuzz, process
def display_recent_investments(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)].sort_values(by='date', ascending=False)
    return temp

def display_biggest_investment(df, investor_name):
    temp = (df[df['investor']
            .fillna('missing')
            .str.contains(investor_name)]
            .sort_values(by='amount', ascending=False)
            .head(1))

    return temp

def display_generally_invests_in(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
    result = (temp
              .groupby('industry_vertical')['date'].count()
              .sort_values(ascending=False)
              .head(1)
              .index[0]
              .title())
    return result


def display_sector_pie(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)]

    data = temp.groupby('industry_vertical')['date'].count().sort_values(ascending=False).head(7).reset_index()
    data.rename(columns={'date': 'num_investments'}, inplace=True)

    # Plot the pie chart using Plotly Express
    fig = px.pie(data, names='industry_vertical', values='num_investments', title='Top Industry Verticals they invest in',
                 hover_data=['industry_vertical'])

    return fig

def display_top_investment_types(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
    data = temp.groupby('investment_type')['date'].count().reset_index()
    data.rename(columns={'date': 'num_investments'}, inplace=True)

    fig = px.pie(data, names='investment_type', values='num_investments', title='Investment round breakdown',
                 hover_data=['investment_type'])

    return fig


def display_top_cities(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
    data = temp.groupby('city')['date'].count().sort_values(ascending=False).head(7).reset_index()
    data.rename(columns={'date': 'num_investments'}, inplace=True)

    fig = px.pie(data, names='city', values='num_investments',
                 title='Top locations the investor(s) have made investments in ',
                 hover_data=['city'])

    return fig


def display_yoy_investment(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
    temp['date'] = pd.to_datetime(temp['date'])
    temp['year'] = temp['date'].dt.year

    required_df = temp.groupby('year')['amount'].sum()
    fig1 = px.line(required_df, x=required_df.index, y=required_df.values, title=' Trend of investment amount over years')
    fig1.update_xaxes(tickvals=required_df.index)
    fig1.update_yaxes(title='amount (in crores INR)')
    fig1.update_layout(
        width=600,  # Specify the width in pixels
        height=400  # Specify the height in pixels
    )

    return fig1

def display_yoy_num_investments(df, investor_name):
    temp = df[df['investor'].fillna('missing').str.contains(investor_name)]
    temp['date'] = pd.to_datetime(temp['date'])
    temp['year'] = temp['date'].dt.year

    # number of investments over years
    new_df = temp.groupby('year')['date'].count()
    fig2 = px.line(new_df, x=new_df.index, y=new_df.values, title='Trend of number of investments over years')
    fig2.update_xaxes(tickvals=new_df.index)
    fig2.update_yaxes(title='number of investments')
    fig2.update_layout(
        width=600,  # Specify the width in pixels
        height=400  # Specify the height in pixels
    )

    return fig2


# display similar startups based on the selected startup name
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



