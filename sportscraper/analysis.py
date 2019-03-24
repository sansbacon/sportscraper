'''
analysis.py

Base class for analyzing sports data

'''

import logging

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns


class SportsAnalysis():
    '''
    Base analysis class

    '''
    def __init__(self, **kwargs):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        sns.set(style="darkgrid")

    
    def facet(self, df, cols, groupcol, hue=None):
        '''
        Creates scatter plot
        
        Args:
            df(DataFrame):
            cols(tuple): x and y
            groupcol(str):
            hue(str):
            
        Returns:
            plot object
            
        '''
        if hue:
            try:    
                return sns.relplot(x=cols[0], y=cols[1], hue=hue, 
                                   data=df, col=groupcol)
            except:
                pass
        return sns.relplot(x=cols[0], y=cols[1], 
                           col=groupcol, data=df);

    def line(self, df, cols):
        '''
        Creates line plot
        
        Args:
            df(DataFrame):
            cols(tuple): x and y
            
        Returns:
            plot object
            
        '''
        return sns.relplot(x=cols[0], y=cols[1], data=df)

    def scatter(self, df, cols, hue=None):
        '''
        Creates scatter plot
        
        Args:
            df(DataFrame):
            cols(tuple): x and y
            hue(str):
            
        Returns:
            plot object
            
        '''
        if hue:
            try:    
                return sns.relplot(x=cols[0], y=cols[1], 
                                   data=df, hue=hue)
            except:
                pass
        return sns.relplot(x=cols[0], y=cols[1], data=df)
        

    def to_df(self, list_of_dict, idx):
        '''
        Creates dataframe from list of dict
        
        '''
        if idx:
            return pd.DataFrame(list_of_dict).set_index(idx)
        return pd.DataFrame(list_of_dict)
        
        
if __name__ == '__main__':
    pass
