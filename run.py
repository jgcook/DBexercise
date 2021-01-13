# -*- coding: utf-8 -*-
"""
Run script for coding exercise
"""
 
import sys
from data_reader import ExampleCSVDataset
from signal_generator import MomentumSignalGenerator, SignalGeneratorConfig
from portfolio_generator import EqualWeightedPortfolioGenerator
from backtesting import WeightedPortfolioBacktester

if __name__ == '__main__':
    # Create signal generator
    config = SignalGeneratorConfig(rolling_avg_days=252)
    signal_generator = MomentumSignalGenerator(config)
    
    # Create portfolio generator
    portfolio_generator = EqualWeightedPortfolioGenerator(signal_generator)
    
    # Load price data into dataframe
    filepath = sys.argv[1]
    dataset = ExampleCSVDataset(filepath)
    prices_df = dataset.read()
    
    # Backtest, generating PnLs and plotting. Export intermediary data
    backtester = WeightedPortfolioBacktester(portfolio_generator, prices_df)
    backtester.execute(export=True)