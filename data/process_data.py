import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    # Load the data files
    """The data file path is provided as arguments in the python script while running the code. This function returns a pandas DataFrame after merging the two data sets"""
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = messages.merge(categories, how = 'outer' , on =['id'])
    return df


def clean_data(df):
    """This function is used to clean data. Categories column is split by special charecter , then new category columns are created with names of the 36 categories and ignoring last two charecters, new columns are then filled with last charecter"""
    categories= pd.Series(df['categories']).str.split(pat = ';', expand= True)
    # select the first row of the categories dataframe
    row = categories.iloc[0]
# use this row to extract a list of new column names for categories.
# one way is to apply a lambda function that takes everything 
# up to the second to last character of each string with slicing
    category_colnames = list(row.apply(lambda x:x[0:-2]))
    categories.columns = category_colnames
    
    for column in categories:
    # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x:x[-1:])
        categories[column] = categories[column].apply(pd.to_numeric)
    # we have few entries in related column as value 2. we need to convert these to 1.
    a = np.array(categories['related'].values.tolist())
    categories['related'] = np.where(a > 1, 1, a).tolist()
    df = df.drop(['categories'], axis = 1)
    
    frames = [df, categories]
    df = pd.concat(frames, axis =1, sort = False)    
    df = df.drop_duplicates()
    return df


def save_data(df, database_filename):
    """Data Frame is stored in the SQlite DB"""
    engine = create_engine('sqlite:///' +database_filename)
    df.to_sql('Project2', engine, index=False)  


def main():
    if len(sys.argv) == 4:
        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]
        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)
        print('Cleaning data...')
        df = clean_data(df)        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
