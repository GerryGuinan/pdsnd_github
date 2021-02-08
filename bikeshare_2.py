import time
import pandas as pd
import numpy as np
import os
from subprocess import call

CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """

    #setting various filters to ''; validation check going through while loop so needs initialising
    city = ''
    month = ''
    day = ''
    data_filter = ''

    print('Hello! Let\'s explore some US bikeshare data!')
    # get user input for city (chicago, new york city, washington). While loop to continuously try and exception handler
    while city not in(CITY_DATA.keys()):
        if city != '':
            print('This is not a valid city name. Please try again')
        try:
            city = input('\nWould you like to see data for Chicago, New York City, or Washington? \n').lower()
        except Exception as e:
                print('Invalid input....try again {}'.format(e))

    #Filter selection - determine if the user wants to filter using different options or none and exception handler
    while data_filter not in(['month','day','both','none']):
        if data_filter != '':
            print('This is not a valid filter selection. Please try again.')
        try:
            data_filter = input('\nFilter by month, day, both or not at all? Enter \"none\" for no filter \n').lower()
        except Exception as e:
                print('Invalid input....try again {}'.format(e))

    # get user input for month (all, january, february, march, april, may, june) and exception handler
    if data_filter == 'month' or data_filter == 'both':
        separator = ", "
        months = ['january', 'february', 'march', 'april', 'may', 'june']
        while month not in(months):
            if month != '':
                print('This is not a valid month selection. Please try again.')
            try:
                #use months list to build user input. any change to list will be reflected input
                month = input('\nSelect month: {}? \n'.format(separator.join([iter.title() for iter in months]))).lower()
            except Exception as e:
                print('Invalid input....try again {}'.format(e))
    else:
        month = 'all'

    # get user input for day of week (all, monday, tuesday, ... sunday)
    if data_filter == 'day' or data_filter == 'both':
        separator = ", "
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday','saturday']
        while day not in(days):
            if day != '':
                print('This is not a valid day selection. Please try again.')
            try:
                #use months list to build user input; any change to list will be reflected input
                day = input('\nSelect day: {}? \n'.format(separator.join([iter.title() for iter in days]))).lower()
            except Exception as e:
                print('Invalid input....try again {}'.format(e))
    else:
        day = 'all'

    print('-'*40)
    return city, month, day, data_filter


def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - pandas DataFrame containing city data filtered by month and day
    """

    #data load can take a couple of seconds, force print with flush otherwise it doesn't print until after load
    print('\nPlease wait a moment....data is loading', flush=True)

    # load data file into a dataframe
    filename = CITY_DATA.get(city,"Error")

    if filename == "Error":
        return "Error: Invalid file. Check city selection"

    try:
        df = pd.read_csv(filename)
    except Exception as e:
        #if an exception is raised, set dataframe to empty and return
        print('\nIssue with import.  File may not exist. Check expected directory for source file')
        df = pd.DataFrame()
        return df

    # convert the Start Time column to datetime
    if df_validate(df.columns, 'Start Time') != 'Error':
        df['Start Time'] = pd.to_datetime(df['Start Time'])

        # extract month and day of week from Start Time to create new columns
        df['month'] = df['Start Time'].dt.strftime("%B")
        df['day_of_week'] = df['Start Time'].dt.strftime("%A")

        # filter by month if applicable
        if month != 'all':
            # use the index of the months list to get the corresponding int
            months = ['january', 'february', 'march', 'april', 'may', 'june']

            # filter by month to create the new dataframe
            df = df[df['month'] == month.title()]

        # filter by day of week if applicable
        if day != 'all':
            # filter by day of week to create the new dataframe
            df = df[df['day_of_week'] == day.title()]
    else:
        return 'Error'

    return df


def time_stats(df, month, day, filter):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    print('You are filtering on: {}'.format(filter))

    """
    Code will check if there are filters.  If the filters are on, popular
    values may already be determined so inform user.

    If there are no filters, checks will identify the most popular
    month, day & hour

    Will also use a group to determine the number of trips
    """

    # display the most common month along with trip count
    if month == 'all':
        popular_month = df['month'].mode()[0]
        print('\nMost popular month: {}   Trips: {}'.format(popular_month, df.groupby('month')['month'].count().max()))
    else:
        print("\nNo popular month stats. You're already filtered on {}".format(month))

    # display the most common day of week along with trip count
    if day == 'all':
        popular_day = df['day_of_week'].mode()[0]
        print('\nMost popular day: {}   Trips: {}'.format(popular_day,df.groupby('day_of_week')['day_of_week'].count().max()))
    else:
        print("\nNo popular day stats.  You're already filtered on {}".format(day.title()))

    # set most popular hour value in the DataFrame
    df['hour'] = df['Start Time'].dt.hour

    # find the most popular hour and also display the trip count
    popular_hour = df['hour'].mode()[0]
    print('\nMost popular hour: {}00 hrs   Trips: {}'.format(popular_hour,df.groupby('hour')['hour'].count().max()))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    if df_validate(df.columns, 'Start Station') != 'Error' and df_validate(df.columns, 'End Station') != 'Error':
        # display most commonly used start station
        print("\nThe most commonly used start station is:{}" .format(df['Start Station'].mode()[0]))

        # display most commonly used end station
        print("\nThe most commonly used end station is:{}" .format(df['End Station'].mode()[0]))

        # create a new value in dataframe with start/end combo
        df['StartEnd'] = 'From "' + df['Start Station'] + '" to "' + df['End Station'] + '"'

        # display most frequent combination of start station and end station trip
        print('Most frequent combination of start station and end station trip: {}'.format(df.groupby('StartEnd')['StartEnd'].count().idxmax()))
        print('Trip frequency for this combination is: {} trips'.format(df.groupby('StartEnd')['StartEnd'].count().max()))
    else:
        print('Either start or end station undefined. Check data set')

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    #travel time is based on trip duration - divisble by 60/60/24 to get days output
    if df_validate(df.columns, 'Trip Duration') != 'Error':
        total_travel_time = df['Trip Duration'].sum() / 60 / 60 /24

        # Calculating years - flat 365 days per year
        years = int(total_travel_time // 365)

        # Calculating months - flat 30 days per month
        months = int((total_travel_time % 365) // 30)

        # Calculating days
        days = int((total_travel_time % 365) % 30)

        # display total travel time
        print('The total travel time for all trips is {} '.format(str(total_travel_time)))
        print('This equates to {} years, {} months and {} days'.format(str(years), str(months), str(days)))

        # display mean travel time
        mean_travel_time = (df['Trip Duration'].mean()) / 60
        print('\nThe average travel time for all trips is {} mins'.format(int(mean_travel_time)))
    else:
        print('Trip Duration undefined in data set')

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def user_stats(df):
    """Displays statistics on bikeshare users"""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # Check if column exists & display counts of user types
    if df_validate(df.columns, 'User Type') != 'Error':
        print('The different user types and the totals:\n')
        print(df.groupby('User Type')['User Type'].count())
    else:
        print('\nUser type is undefined in data')

    # Check if column exists & display counts of gender
    if df_validate(df.columns, 'Gender') != 'Error':
        print('\n\nThe different gender types and the totals:\n')
        print(df.groupby('Gender')['Gender'].count())

        print('Undefined gender total is: {}'.format(df['Gender'].isnull().sum()))
    else:
        print('\nGender type undefined in data')

    # Display earliest, most recent, and most common year of birth
    if df_validate(df.columns, 'Birth Year') != 'Error':
        print('\n....and finally some birth related statistics')

        print('\nThe earliest birth year in the set is: {}'.format(int(df['Birth Year'].min())))
        print('\nAnd the latest birth year in the set is: {}'.format(int(df['Birth Year'].max())))
        print('\nFinally...the most common birth year is: {}'.format(int(df['Birth Year'].mode()[0])))
    else:
        print('\nBirth Year undefined in data')


    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)

def df_validate(df_col, column_name):
    """
    Almost not enough to justify a function, but storing here because of
    continuous checking. This can also future proof; perform all dataframe checks
    in here as they're identified
    """

    if column_name not in df_col:
        return "Error"


def clear_screen():
    """
    Check for the os name to determine the clear screen command to run

    Doesn't work on bash shell from Windows because it's expecting to send a
    dos command which bash doesn't recognise
    Trap the error and print 10 blank lines instead
    """
    try:
        if os.name =='nt':
            _ = call('cls')
        else:
            _ = call('clear')
    except Exception as e:
        print("\n"*10)

def record_scroll(df):

    """
    Option for users to scroll through individual records in data set
    Scroll through the data set 5 records at a time; return when eof or user selects
    Iter variable initialised outside, count through records for option to break

    """
    iter = 0
    for index, row in df.iterrows():
        print('Row Index: {}'.format(index))
        print(type(row))
        print(row)
        print('------')

        #add 1 through each iteration; if modulo 5 == 0, allow user to break
        iter += 1
        if iter % 5 == 0:
            more_rec = input('Would you like to continue viewing records. Enter \'yes\' or \'no\'.\n')
            if more_rec != 'yes':
                return

def main():

    #clear screen os call; sucsess depends on os type
    clear_screen()

    while True:
        city, month, day, data_filter = get_filters()
        df = load_data(city, month, day)

        #check if the returned dataframe is empty before running stats
        if df.empty:
            print('Returned data set is empty. Check file names and file structure before proceeding.')
        else:
            time_stats(df, month, day, data_filter)
            station_stats(df)
            trip_duration_stats(df)
            user_stats(df)

            #record_scroll function provides ability to scroll through individual records
            view_recs = input('\nWould you like to view individual records? Enter \'yes\' or \'no\'.\n')
            if view_recs == 'yes':
                record_scroll(df)

        restart = input('\nWould you like to restart? Enter \'yes\' or \'no\'.\n')

        if restart.lower() != 'yes':
            break

        clear_screen()

if __name__ == "__main__":
	main()
