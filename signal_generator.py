# -*- coding: utf-8 -*-
"""
Defines signal generator classes
"""

import abc


class SignalGeneratorConfig:
    '''
    Holds options that can be used to configure signal generators.
    Currently doesn't do much but could be useful for saving metadata/reproducibility.
    '''
    
    def __init__(self, **generator_params):
        '''
        Constructor for SignalGeneratorConfig.
        Using **params for now but should probably be less flexible - depends on use cases
        
        param generator_params: kwargs - options for signal generator
        '''
        
        self.params = generator_params


class SignalGenerator(abc.ABC):
    '''
    Signal generator base class.
    SignalGenerator subclasses take in price data and output signal data according to their _prices_to_signal method.
    '''
    
    def __init__(self, generator_config):
        '''
        Constructor for SignalGenerator
        
        param generator_params: kwargs - options for signal generator
        '''
        
        self._cfg = generator_config
        self._validate_config_params()
    
    def generate(self, prices_df):        
        '''
        Use the provided prices dataframe to generate a signal.
        Example output:
                         Asset_1   Asset_2   Asset_3    
            2000-01-03  0.138743  0.124195  0.053917   
            2000-01-05  0.011134  0.022408 -0.005815  
            2000-01-06  0.064087  0.075680  0.049160  
        
        param prices_df: pandas.DataFrame - dataframe containing historical prices
        returns: pandas.DataFrame - dataframe containing signal data
        '''
        
        signal_df = self._prices_to_signal(prices_df)
        return signal_df
    
    def _validate_config_params(self):
        '''
        Checks that all parameters required for the SignalGenerator subclass were provided in the initialisation.
        Raises an error if any parameter is missing.
        '''
        
        missing_params = self._required_params.difference(self._cfg.params)
        if missing_params:
            raise Exception('%s must be initialised with kwargs specifying: %s' % (type(self).__name__, missing_params))
    
    @abc.abstractmethod
    def _prices_to_signal(self, prices_df):
        '''
        Subclasses must specify how to obtain signals from price data.
        
        param prices_df: pandas.DataFrame - dataframe containing historical prices
        '''
        
        pass
    
class MomentumSignalGenerator(SignalGenerator):
    '''
    Use a rolling mean approach to generate a momentum signal.
    Requires an integer rolling_avg_days param in the config.
    '''
    
    _required_params = {'rolling_avg_days'}
   
    def _prices_to_signal(self, prices_df):
        '''
        Use a rolling mean approach to generate a momentum signal.
        
        param prices_df: pandas.DataFrame - dataframe containing historical prices
        returns: pandas.DataFrame containing signal data
        '''
        
        window = '%sd' % self._cfg.params['rolling_avg_days']
        return prices_df.pct_change().rolling(window).mean()
    

