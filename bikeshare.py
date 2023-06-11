import time
import pandas as pd
import numpy as np

CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

# declaring the month and day lists for list for refernce
months = ['january', 'february', 'march', 'april', 'may', 'june']
days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

def check_entry(prompt, valid_entries):
    while True:
        try:
            entry = str(input(prompt)).lower() if type(valid_entries[0]) == str else int(input(prompt)) # Get user input

            while entry not in valid_entries: # Prompt the user again if an invalid entry is given
                print("Invalid input provided.  Input should either be: ",
                    ", ".join(str(x) for x in valid_entries),".")
                entry = str(input(prompt)).lower() if type(valid_entries[0]) == str else int(input(prompt))

            return entry
        except ValueError:
            print('ValueError raised. Please enter {}.'
                  .format("an integer" if type(valid_entries[0]) == int else "a string"))

def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    print('Welcome! Explore the dataset on US Bikeshare Usage.',
         '\nWe have data on the following cities: Chicago, New York City, and Washington.')
    # get user input for city (chicago, new york city, washington). HINT: Use a while loop to handle invalid inputs
    while True:
        city = str(input('Would you like to see data for Chicago, New York City, or Washington?\n')).lower()
        if city.lower() not in ['chicago','new york city','washington']:
            print('Invalid city provided.')
        else:
            break

    # get use input for how the data should be filtered
    while True:
        filter_options = str(input('Would you like to filter the data by month, day, all or none?\n')).lower()
        if filter_options.lower() not in ['month','day','all','none']:
            print('Invalid answer. Input should either be: month, day, all, or none.')
        else:
            break
    # assigning 'none' to month and day of the week for when the user does not want to filter for anything
    if filter_options == 'none': 
        month = 'none'
        day = 'none'
    elif filter_options == 'month': # get user input for month (all, january, february, ... , june)
        while True:
            month = str(input('Which month: January, February, March, April, May, or June?\n')).lower()
            if month not in ['january', 'february', 'march', 'april', 'may', 'june']:
                print('Invalid month. Please type the full name of the month.')
            else:
                day = 'none'
                break
    elif filter_options == 'day': # get user input for day of week (all, monday, tuesday, ... sunday)
        while True:
            try:
                day = int(input('Which day? Insert a number between 0 and 6 (Monday = 0 and Sunday = 6).\n'))
                if day not in [0, 1, 2, 3, 4, 5, 6]:
                    print('Invalid day selected.')
                else:
                    month = 'none'
                    break
            except ValueError:
                print('Invalid format. Insert an Integer between 0 and 6.')
            
    elif filter_options == 'all': # get user input for both day of week and month
        while True:
            month = str(input('Which month: January, February, March, April, May, or June?\n')).lower()
            if month not in ['january', 'february', 'march', 'april', 'may', 'june']:
                print('Invalid month. Input should either be January, February, March, April, May, or June.')
            else:
                break
        while True:
            try:
                day = int(input('Which day? Insert a number between 0 and 6 (Monday = 0 and Sunday = 6)\n'))
                if day not in [0, 1, 2, 3, 4, 5, 6]:
                    print('Invalid day selected.')
                else:
                    month = 'none'
                    break
            except ValueError:
                print('Invalid format. Insert an Integer between 0 and 6.')
            
    print('-'*79)
    return city, month, day

def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.
    Assess the data for any missing or duplicated values.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """
    print('Loading the {} Bikeshare Data Filtered for Month: {}, Day: {}.'
          .format(city.title(), month.title(),
                  day.title() if day == 'none' else days[day].title()))
    # get the file name for the dictionary CITY_DATA to load the dataset
    df = pd.read_csv(CITY_DATA[city])
    
    # convert the Time columns to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])
    
    # Data Quality Assessment
    if city != 'washington':
        # The Gender and Birth Year values are primarily missing for User Type: Customer
        # The customers with missing values form about 99% of the data on this user type
        # Removing the missing values would skew the analysis againt Customers
        df['Gender'] = df['Gender'].fillna('Unknown')
        df['Birth Year'] = pd.to_numeric(df['Birth Year'], errors='coerce', downcast='integer')
        # 107-year-old Robert Marchand participated in a 4,000-meter track cycling race
        # He set the record for cyclists over 105 and is therefore an outlier
        # We'll assume that anyone older than that is probably a data capturing error
        df = df[(df['Birth Year'] >= 1912) | (pd.isnull(df['Birth Year']))]
        df['Age'] = df['Start Time'].dt.year - df['Birth Year']
    
    # create the month, day of week, & hour columns from the Start Time column
    df['Month'] = df['Start Time'].dt.month
    df['DayofWeek'] = df['Start Time'].dt.dayofweek
    df['Hour'] = df['Start Time'].dt.hour
    df['Hour'] = pd.to_datetime(df['Hour'], format='%H').dt.strftime('%H:%M:%S')    
    
    # Create the 'Combination Station' column from the start and end station
    df['Combination Stations'] = df['Start Station'] + ' - ' + df['End Station']
    
    # filter by month if applicable
    if month != 'none':
        # use the index of the months list to get the corresponding int
        months = ['january', 'february', 'march', 'april', 'may', 'june']
        month = months.index(month) + 1
        df = df[df['Month'] == month]
    # filter by day of week if applicable
    if day != 'none':
        # use the index of the days list to get the corresponding int
        df = df[df['DayofWeek'] == day]
    
    print('The Bikeshare System Recorded {} Trips between {} & {}.'
          .format(len(df), df['Start Time'].dt.date.min(),
                  df['Start Time'].dt.date.max()))
    
    return df

def user_stats(df):
    """
    Displays statistics on bikeshare users.
    
    Args:
        df - Pandas DataFrame containing city data filtered by month and day
    """

    print('\nCalculating User Statistics...\n')
    start_time = time.time()
    
    # Display counts of user types
    unique_usertype = df['User Type'].value_counts()
    print('User Type Counts:')
    for usertype, count in zip(unique_usertype.index, unique_usertype):
        print('{:11}: {}'.format(usertype, count))
    
    print('\nGender Count:')
    try:
        # Display counts of gender
        unique_gender = df['Gender'].value_counts()
        for gender, count in zip(unique_gender.index, unique_gender):
            print('{:8}: {}'.format(gender, count))
    except KeyError:
        print("Data on Users' Gender is not Available.")
    
    print("\nUsers' Birth Year Statistics:")
    try:
        # Display earliest, most recent, and most common year of birth
        print("Youngest User : {:2} - {} years old\nOldest User   : {:2} - {} years old".
              format(int(max(df['Birth Year'])), int(min(df['Age'])),
                     int(min(df['Birth Year'])), int(max(df['Age']))))

    except KeyError:
        print("Data on Users' Birth Year is not Available.")

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*79)

def time_stats(df):
    """
    Displays statistics on the most frequent times of travel.
    
    Args:
        df - Pandas DataFrame containing city data filtered by month and day
    """

    print('\nCalculating Trends in City Bike Usage\n',
          '\nTrends in the Times that Users Choose to Travel...')
    start_time = time.time()
        
    # display the most common month
    print('Popular Month to Travel: {:8}    Number of Trips: {}'.
          format(months[df['Month'].value_counts().index[0] - 1].title(),
                 df['Month'].value_counts().iloc[0]))

    # display the most common day of week
    print('Popular Weekday to Travel: {:8}    Number of Trips: {}'.
          format(days[df['DayofWeek'].value_counts().index[0]].title(),
                 df['DayofWeek'].value_counts().iloc[0]))

    # display the most common start and end hour
    print('Popular Hour to Travel : {:8}    Number of Trips: {}'.
          format(df['Hour'].value_counts().index[0],
                 df['Hour'].value_counts().iloc[0]))
    
    # display the least popular start hour
    print('Hour with the Lowet Number of Trips: {:8}    Number of Trips: {}'.
          format(df['Hour'].value_counts().index[-1],
                 df['Hour'].value_counts().iloc[-1]))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*79)

def station_stats(df):
    """
    Displays statistics on the most popular stations and trip.
    
    Args:
        df - Pandas DataFrame containing city data filtered by month and day
    """

    print('\nTrends in Stations and Travel Routes Used...\n')
    start_time = time.time()
              
    # display most commonly used start station
    print('Popular Start Station: {}    Number of Trips: {}'
          .format(df['Start Station'].value_counts().index[0],
                  df['Start Station'].value_counts()[0]))
    
    # Display the start station with the lowest number of trips
    print('Least Popular Start Station: {}    Number of Trips: {}'
          .format(df['Start Station'].value_counts().index[-1],
                  df['Start Station'].value_counts().iloc[-1]))
    
    # display most commonly used end station
    print('Popular End Station: {}    Number of Trips: {}'
          .format(df['End Station'].value_counts().index[0],
                  df['End Station'].value_counts().iloc[0]))

    # Display the end station with the lowest number of trips
    print('Least Popular End Station: {}    Number of Trips: {}'
          .format(df['End Station'].value_counts().index[-1],
                  df['End Station'].value_counts().iloc[-1]))
    
    # display most frequent combination of start station and end station trip
    print ('The Most Frequent Combination of Start Station and End Station:\n'+
        'Start Station: {}\nEnd Station: {}'
           .format(df['Combination Stations'].value_counts().index[0].split(' - ')[0],
                   df['Combination Stations'].value_counts().index[0].split(' - ')[1]))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*79)

def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration.
    
    Args:
        df - Pandas DataFrame containing city data filtered by month and day
    """

    print('\nTrends in Trip duration...\n')
    start_time = time.time()

    # display the minimum travel time
    print('Minimum Travel Time: {} {}'
          .format(round(df['Trip Duration'].min() / 60),
                  'minute' if round(df['Trip Duration'].min() / 60) == 1.0 else 'minutes'))
    
    # display mean travel time
    print('Average Travel Time: {} minutes'.format(round(df['Trip Duration'].mean() / 60)))

    # display the maximum travel time
    print('Maximum Travel Time: {:,} minutes'.format(round(df['Trip Duration'].max() / 60)))
    
    # display total travel time
    print('Total Travel Time: {:,} minutes'.format(round(df['Trip Duration'].sum() / 60)))
    
    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*79)

def relative_duration_stats(city, df):
    """
    Provides relevent additional statistics:
    Trip duration in relation to start station, user type, gender, and age
    
    Args:
        df - Pandas DataFrame containing city data filtered by month and day
    """
    print('\nAdditional Statistics...\n')
    start_time = time.time()
    
    # Group the dataset by start station to get the average trip duration
    df_by_trip_duration = (df.groupby('Start Station')['Trip Duration']
                           .mean().sort_values(ascending=False))
    
    # display the top three start stations with the highest trip duration
    print('Top Three stations with the highest average trip duration:',
          '\n{}: {} minutes\n{}: {} minutes\n{}: {} minutes'
          .format(df_by_trip_duration.index[0], round(df_by_trip_duration.iloc[0] / 60),
                  df_by_trip_duration.index[1], round(df_by_trip_duration.iloc[1] / 60),
                  df_by_trip_duration.index[2], round(df_by_trip_duration.iloc[2] / 60)))
    
    # Group the dataset by user type to get their respective trip duration
    df_by_user = (df.groupby('User Type')['Trip Duration']
                  .mean().sort_values(ascending=False))
    
    # Display the average trip duration for each recorded user type
    print('\nAverage Trip Duration by User Type:')
    for user, duration in zip(df_by_user.index, df_by_user):
            print('{:10}: {} minutes'.format(user, round(duration / 60)))
            
    if city != 'washington':        
        # Group the dataset by gender to get their respective trip duration
        df_by_gender = (df.groupby('Gender')['Trip Duration']
                        .mean().sort_values(ascending=False))
        
        # Display the average trip duration for each recorded gender
        print('\nAverage Trip Duration by Gender:')
        for gender, duration in zip(df_by_gender.index, df_by_gender):
                print('{:8}: {} minutes'.format(gender, round(duration / 60)))
                
        # Display the correlation between trip duration and age
        print('\nCorrelation between Trip Duration and Age: {}'
              .format(df.corr().loc['Trip Duration', 'Age']))
    
    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*79)

def individual_data(city, start):
    """
    Provides the raw individual data of 5 users.
    
    Args:
      (str) City - name of city being analysed
      (int) start - numerical index
    """
    # retrieve the raw dataset
    df = pd.read_csv(CITY_DATA[city])
    
    # Print the dictionary in the desired format
    n = 5
    while n > 0:
        for key, value in df.iloc[start].to_dict().items():
            print(f"{key}: {value}")
        print('-'*79)
        start += 1
        n -= 1

def main():
    while True:
        city, month, day = get_filters()
        df = load_data(city, month, day)
        
        if len(df) > 0: # For when df is empty
            user_stats(df)
            time_stats(df)
            station_stats(df)
            trip_duration_stats(df)
            relative_duration_stats(city, df)
            
            # diplay raw data to user if requested
            i = 0
            while True:
                view_data = str(input("\nWould you like to view 5 Users' trip data? (yes/no)\n"))
                if view_data not in ['yes', 'no']:
                    print('Invalid input. Enter yes or no.')
                elif view_data == 'yes':
                    individual_data(city, i)
                else:
                    break
                i += 5
        else:
            print('Filtered dataset is empty. Restart the program to select new filters.')

        restart = input('\nWould you like to restart? Enter yes or no.\n')
        if restart.lower() != 'yes':
            break

if __name__ == "__main__":
	main()
