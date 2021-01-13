# -*- coding: utf-8 -*-
"""
Defines PortfolioGenerator classes.
"""

import pandas as pd
import numpy as np
import abc

class WeightedPortfolioGenerator(abc.ABC):
    '''
    WeightedPortfolioGenerator generates a portfolio weighting for all assets, given a set of price data and a signal generator.
    '''
    
    def __init__(self, signal_generator, rebalance_period='1M', longshort_split=0.5):
        '''
        Constructor for WeightedPortfolioGenerator.
        
        param signal_generator: signal_generator.SignalGenerator subclass - signal generator object
        param rebalance_period: str - rebalance period as a frequency string.
        param longshort_split: float - determines proportion of long vs short positions
        '''
        
        self._signal_generator = signal_generator
        self._rebalance_period = rebalance_period
        self._longshort_split = longshort_split

    def generate_weights(self, prices_df, save_for_exporting=False):
        '''
        Use signal generator and price data to generate weights.
        Process:
            - Use signal generator to generate signal data
            - Rank signal data at monthly intervals
            - Assign long/short positions based on ranking
            - Assign weights
        
        Example output:
                         Asset_1   Asset_2   Asset_3    
            2000-01-01  0.111111  0.111111  0.111111
            2000-02-01  0.111111 -0.111111 -0.111111
            2000-03-01 -0.111111  0.111111  0.111111
            
        param prices_df: pandas.DataFrame - dataframe containing historical price data
        param save_for_exporting: bool - if True, store intermediary data for later exporting
        returns: pandas.DataFrame containing daily weights
        '''
        
        # Use signal generator to generate signal data
        signal_df = self._signal_generator.generate(prices_df)
        # Rank signal data at monthly intervals
        rank_df = self._rank_signals(signal_df)
        # Assign long/short positions based on ranking
        longshort_portfolios = self._assign_longshort(rank_df)
        # Assign asset weights based on ranking
        weights = self._assign_weights(longshort_portfolios)
        # Upsample to daily weight data
        daily_weights = weights.reindex(prices_df.index, method='bfill')
        
        if save_for_exporting:
            # Need to export intermediary data. Keeping dataframes in an attribute so they can be exported later
            self.export_data = {'signal_df': signal_df,
                                'rank_df': rank_df,
                                'daily_weights': daily_weights,
                                'longshort_portfolios': longshort_portfolios}
        
        return daily_weights

    def _rank_signals(self, signal_df):
        '''
        Generate table of asset rankings based on their signals for each date
        
        param signal_df: pandas.DataFrame - dataframe containing signal data
        returns: pandas.DataFrame containing asset rankings for each date
        '''
        # get signal at the start of each month
        monthly_signal = signal_df.resample(self._rebalance_period).first() 
        rank_df = monthly_signal.rank(axis=1, ascending=False, method='first') # have to use method=first to avoid non-integer ranks
        return rank_df        
    
    def _assign_longshort(self, rank_df):
        '''
        Designate positions as long or short based on their ranking.
        
        param rank_df: pandas.DataFrame - dataframe containing asset rankings 
        returns: pandas.DataFrame with long positions assigned +1, short positions assigned -1
        '''
        cutoff = rank_df.shape[1] * self._longshort_split
        # Determine which positions are ranked below cutoff
        longshort_portfolios = pd.DataFrame(np.where(rank_df <= cutoff, 1, -1), 
                                            index=rank_df.index, 
                                            columns=rank_df.columns)
        return longshort_portfolios
        
    @staticmethod
    @abc.abstractmethod
    def _assign_weights(longshort_portfolios):
        '''
        Subclasses must define how to assign weights based on long/short information.
        
        param longshort_portfolios: pandas.DataFrame - dataframe with long positions assigned +1, short positions assigned -1
        '''
        
        pass

class EqualWeightedPortfolioGenerator(WeightedPortfolioGenerator):
    @staticmethod
    def _assign_weights(longshort):
        '''
        Assign weights based on whether the position is long/short.
        Inside each leg the weights are equal and must sum to 1.
        '''
        # Determine weight for each leg
        long_leg_weights = 1 / (longshort > 0).sum(axis=1)
        short_leg_weights = 1 / (longshort < 0).sum(axis=1)
        # Apply weights to long/short position data
        weight_factors = np.where(longshort > 0, longshort.mul(long_leg_weights, axis=0), longshort.mul(short_leg_weights, axis=0))
        weighted_portfolios = pd.DataFrame(weight_factors, index=longshort.index, columns=longshort.columns)
        return weighted_portfolios
