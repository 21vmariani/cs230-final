"""
Vincenzo Mariani
cs230-4
correct_lat_lng_mass_shootings_final_20171116_835.csv
url:

"""

# Use license in file
import us_state_abbrev as sa
import pandas as pd
import altair as alt
import folium
import streamlit as st
from streamlit_folium import st_folium


def get_data():
    """
    Load the data file - this could be improved by allowing the user to choose the file
    :return: a dataframe with the csv file loaded
    """
    return pd.read_csv("./correct_lat_lng_mass_shootings_final_20171116_835.csv")


def get_years(df):
    """

    :param df: a Dataframe containing a series of 'Date's
    :return: a dataframe containing a unique list of years from the min -> max dates only years in the data
    """
    df['Year'] = pd.to_datetime(df['Date']).dt.year

    min_year = df['Year'].min()
    max_year = df['Year'].max()
    all_years = pd.DataFrame({'Year': range(min_year, max_year + 1)})
    return all_years


def page_layout(choices, years):
    """
    Page layout and navigation - sidebar, title, header and footer

    :param choices: a list of possible pages
    :param years: Year range for dynamic title
    :return: the page chosen from the list of pages
    """

    st.set_page_config(page_title="Final Project- Display Data on Mass Shootings", page_icon=":fire:")
    main_pg = st.container()

    with st.sidebar:
        st.header("CS230 Final Project by\nVincenzo Mariani")
        st.subheader("Navigation:")
        page = st.radio('Please select a page', choices)

    with main_pg:
        st.title("Mass Shootings (" + str(years['Year'].min()) + ' - ' + str(years['Year'].max()) + ")")

        # clean up the page - hide streamlit menus and soften the background to a grey
        # learned this via YouTube
        st_style = """
            <style>
            .main {
            background-color: #f4f4f4
            }
            #MainMenu {visibility: hidden}
            footer {visibility: hidden}
            </style>
            """
        st.markdown(st_style, unsafe_allow_html=True)
    return page


def show_data(df_mass_shootings):
    """
    Mindless table to refer back for detail and debug.

    :param df_mass_shootings: Dataframe containing the input data
    :return: none
    """
    # original data set
    st.write("This is the original dataset")
    st.write(df_mass_shootings)


def lineplot_mass_shootings(df_mass_shootings, all_years):
    """
    Display a lineplot of shootings by year

    :param df_mass_shootings: a dataframe containing the input data
    :param all_years: a dataframe containing the years to plot
    :return: None
    """
    # extract the year from the Date column
    df_mass_shootings['Year'] = pd.to_datetime(df_mass_shootings['Date']).dt.year

    # count the occurrences of each year and sort by year
    year_counts = df_mass_shootings['Year'].value_counts().reset_index().rename(columns={
        'index': 'Year', 'Year': 'Count'}).sort_values(by='Year')

    # create a new DataFrame with all years between min and max year
    # needed to include years with zero data entries
    all_years_counts = pd.merge(all_years, year_counts, on='Year', how='left').fillna(0)

    # plot the counts over time using altair, used altair sources
    line = alt.Chart(all_years_counts).mark_line(strokeWidth=5).encode(
        x=alt.X('Year', axis=alt.Axis(format='d', tickCount=30, labelAngle=-45, labelPadding=5,
                                      labelFlush=False, labelOverlap=False, labelSeparation=5), title='Year'),
        y=alt.Y('Count', title='Number of Mass Shootings'),
        tooltip=['Year', 'Count']
    ).properties(
        title='Number of Mass Shootings per year ' + str(df_mass_shootings['Year'].min()) + ' - ' + str(
            df_mass_shootings['Year'].max())
    ).interactive()

    # display the plot in Streamlit
    st.altair_chart(line, use_container_width=True)


def map_mass_shootings(df, map, start_year=0, end_year=(-1)):
    """
    place markers on map and render it

    :param df: a Dataframe containing the input data
    :param map: a Folium map object to put the markers
    :param start_year: first year to start summarizing data
    :param end_year: last year in range for summary - default action is only the start year
    :return: none
    """
    # quick error check
    if start_year == 0:
        st.write("year not selected")
        return

    # only 1 year
    if end_year == (-1):
        end_year = start_year

    # filter the dataframe by year
    df_year = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

    count = 0
    # add markers for each mass shooting location, stremlit-folium website was helpful
    for index, row in df_year.iterrows():
        count += 1
        folium.Marker(location=[row['Lat'], row['Lng']], tooltip=f"{row['Event']} ({row['Date']}) "
                                                                 f"({row['Location']})").add_to(map)
    if count == 0:
        st.write("There were no mass shootings during this time frame")
        return
    elif start_year == end_year:
        st.write("This map locates the", str(count), " mass shooting(s) which occurred in the year: ", str(start_year))
    else:
        st.write("This map locates the", str(count), " mass shooting(s) which occurred between the years: ",
                 str(start_year), " and ", str(end_year))

    # display the map in Streamlit
    st_folium(map, width=800, returned_objects=[])


# single year -
def user_select_year(df, all_years):
    """
    Selection Box for choosing 1 year

    :param df: a Dataframe containing the input data
    :param all_years: A dataframe containing unique list of years from input data
    :return: none
    """
    # create a drop-down menu for the years
    year_selected = st.selectbox('Select a year:', all_years)

    m = folium.Map(location=[39.05, -94.710], zoom_start=4)

    # call the function to display the map for the selected year
    map_mass_shootings(df, m, year_selected)


# Multiple years
def user_select_years_slider(df, all_years):
    """
    Selection slider for choosing a range of years
    Thought having slider with two ends was cool, was part of my proposal so happy it came to be
    :param df: a Dataframe containing the input data
    :param all_years: A dataframe containing unique list of years from input data
    :return: none:
    """

    # how do I remember the last value if user leaves to another page and returns? didn't understand how to cache
    # input
    year_range = st.slider('Select an inclusive range of years', int(all_years['Year'].min()),
                           int(all_years['Year'].max()),
                           (int(all_years['Year'].min()), int(all_years['Year'].max())))
    # map
    m = folium.Map(location=[39.05, -94.711], zoom_start=4)

    map_mass_shootings(df, m, year_range[0], year_range[1])


def display_state_data(df):
    """
    Data summarized by state
    do some text analysis on the location series
    convert to state abbreviations
    The amount of user input for this is cool that changes how the data is presented

    :param df: dataframe
    :return:
    """
    # imported sa to help converting state names and abbreviations
    # Very COOL list comprehension to initialize my state counts

    state_counts = dict((s, int(0)) for s in sa.abbrev_to_us_state.keys())

    for index, row in df.iterrows():
        # grabs just states
        state = row['Location'].split(",")[1].strip()
        if state in sa.us_state_to_abbrev:
            # changes full name to abbreviation
            ssa = sa.us_state_to_abbrev[state]
            # counts amount per state
            state_counts.update({ssa: (state_counts[ssa] + 1)})
        elif state in sa.abbrev_to_us_state:
            # counts amount per state
            state_counts.update({state: (state_counts[state] + 1)})
        else:
            st.write('Error: State not found in state list (' + state + ')')
            return

    # user input options
    options = ["Sort by State", "Sort by Count"]
    sort_by = st.radio("Please select a way to sort, and any options", options)

    reverse_sort = st.checkbox("Reverse sort")
    no_zero = st.checkbox("Remove zeros")
    if no_zero:
        state_counts = {x: y for x, y in state_counts.items() if y != 0}

    if sort_by == options[0]:
        stateKeys = list(state_counts.keys())
        # sorts list of keys
        stateKeys.sort(reverse=reverse_sort)
        # create a sorted dictionary
        sorted_state = {i: [state_counts[i]] for i in stateKeys}
        df_ss = pd.DataFrame.from_dict(sorted_state, orient='index', columns=['Count'])
        st.write(df_ss)
    elif sort_by == options[1]:
        # sort values
        sorted_state_by_count = sorted(state_counts.items(), key=lambda x: x[1], reverse=reverse_sort)
        df_sd = pd.DataFrame(sorted_state_by_count, columns=['State', 'Count'])
        st.write(df_sd)


def main():
    """
    Get data and manage page selection

    :return: 0 if doesn't error
    """

    df_mass_shootings = get_data()

    df_years = get_years(df_mass_shootings)

    choices = ['Input data', 'Line Plot', 'Maps', 'States']

    display = page_layout(choices, df_years)

    if display == choices[0]:
        show_data(df_mass_shootings)
    elif display == choices[1]:
        lineplot_mass_shootings(df_mass_shootings, df_years)
    elif display == choices[2]:
        user_select_year(df_mass_shootings, df_years)
        user_select_years_slider(df_mass_shootings, df_years)
    elif display == choices[3]:
        display_state_data(df_mass_shootings)
    else:
        st.write('Page selection failed')

    return 0


# check if this was imported or ran as the main program
if __name__ == '__main__':
    main()
