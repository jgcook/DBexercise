# -*- coding: utf-8 -*-
"""
Defines backtesting classes.
"""


class WeightedPortfolioBacktester:      
    '''
    Class designed for backtesting WeightedPortfolioGenerators
    '''
    
    def __init__(self, portfolio_generator, prices_df):
        '''
        Constructor for WeightedPortfolioBacktester.
        
        param portfolio_generator: portfolio_generator.WeightedPortfolioGenerator object
        param prices_df: pandas.DataFrame - dataframe containing historical price data
        '''
        
        self._portfolio_generator = portfolio_generator
        self._prices_df = prices_df
      
    def execute(self, export=False, figsize=(11,9)):
        '''
        Run backtesting.
        Process:
            - Generate portfolio weights using portfolio_generator
            - Use weights to determine asset PnLs
            - Determine total PnL and plot
            - if export=True, export previously stored intermediary data
        
        param export: bool - if True, export previously stored intermediary data as CSVs
        param figsize: tuple of ints - determines size of plotted total PnL figure
        '''
        
        # Generate portfolio weights using portfolio_generator
        daily_weights = self._portfolio_generator.generate_weights(self._prices_df, save_for_exporting=export)
        
        #Use weighted portfolio to determine asset PnLs & total PnL
        asset_pnls, total_pnl = self._get_pnls(daily_weights)
        
        # Plot figure & save
        ax = total_pnl.plot(figsize=figsize, grid=True)
        ax.set(xlabel='Date', ylabel='PnL')
        ax.get_figure().savefig('pnl.png')
        
        if export:
            # Export data if desired
            self._export_intermediary_data()

    def _get_pnls(self, daily_weights):
        '''
        Calculate PnL for each asset based on portfolio weights, then sum up to work out the total.
        
        param daily_weights: pandas.DataFrame - dataframe containing daily portfolio weights
        returns: pandas.DataFrame containing PnLs for each asset
        '''
        
        assets_daily_pct_change = self._prices_df.pct_change()
        asset_pnls = (1 + (daily_weights * assets_daily_pct_change)).cumprod() - 1
        total_pnl = asset_pnls.sum(axis=1)
        return asset_pnls, total_pnl
    
    def _export_intermediary_data(self):
        '''
        Export previously stored intermediary data
        '''
        
        self._portfolio_generator.export_data['signal_df'].to_csv('momentumSignal.csv')
        self._portfolio_generator.export_data['rank_df'].to_csv('momentumRanks.csv')
        self._portfolio_generator.export_data['longshort_portfolios'].to_csv('LongShortPositions.csv')
        self._portfolio_generator.export_data['daily_weights'].to_csv('weights.csv')
        

