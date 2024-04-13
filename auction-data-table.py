
import numpy as np
import pandas as pd
import treasury_gov_pandas

df = treasury_gov_pandas.update_records('https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query')

# print(df.iloc[0].to_string())

# print(df.iloc[-10].to_string())

df['auction_date'] = pd.to_datetime(df['auction_date'])

df['bid_to_cover_ratio']       = pd.to_numeric(df['bid_to_cover_ratio'],       errors='coerce')
df['direct_bidder_accepted']   = pd.to_numeric(df['direct_bidder_accepted'],   errors='coerce')
df['indirect_bidder_accepted'] = pd.to_numeric(df['indirect_bidder_accepted'], errors='coerce')

df['comp_accepted']            = pd.to_numeric(df['comp_accepted'], errors='coerce')

def show_concise_basic(df):
    print(df[['auction_date', 'security_type', 'security_term', 'original_security_term', 'tips', 'bid_to_cover_ratio']].sort_values(by=['auction_date']).to_string())

# show_concise_basic(df.tail(25))

def show_concise(df):
    print(df[['auction_date', 'security_type', 'security_term', 'original_security_term', 'bid_to_cover_ratio', 'bid_to_cover_ratio_pct_change']].to_string())

def show_concise_alt(df):
    print(df[['auction_date', 'security_type', 'security_term', 'original_security_term', 'bid_to_cover_ratio', 'bid_to_cover_ratio_pct_change', 'days_since_lower_or_higher']].to_string())

# ----------------------------------------------------------------------

# original_security_term = '20-Year'
# tips = 'No'

def auction_table(original_security_term, tips):

    df_sub = df[df['original_security_term'] == original_security_term]

    df_sub = df_sub[df_sub['tips'] == tips]

    df_sub['direct_pct_of_competitive']   = df_sub['direct_bidder_accepted']   / df_sub['comp_accepted']
    df_sub['indirect_pct_of_competitive'] = df_sub['indirect_bidder_accepted'] / df_sub['comp_accepted']
    
    
    df_sub['bid_to_cover_ratio_pct_change']       = df_sub['bid_to_cover_ratio'].pct_change()
    df_sub['direct_bidder_accepted_pct_change']   = df_sub['direct_bidder_accepted'].pct_change()
    df_sub['indirect_bidder_accepted_pct_change'] = df_sub['indirect_bidder_accepted'].pct_change()

    df_sub['bid_to_cover_ratio_days']       = np.nan
    df_sub['direct_bidder_accepted_days']   = np.nan
    df_sub['indirect_bidder_accepted_days'] = np.nan
                    
    for i in range(1, len(df_sub)):

        def inner(field, pct_change, days_since):

            if df_sub[pct_change].iloc[i] < 0:

                lower_values = df_sub[df_sub[field] < df_sub[field].iloc[i]]

                previous_lower_values = lower_values[lower_values['auction_date'] < df_sub['auction_date'].iloc[i]]
                    
                if not previous_lower_values.empty:
                    df_sub[days_since].iloc[i] = (df_sub['auction_date'].iloc[i] - previous_lower_values['auction_date'].iloc[-1]).days            
        
            if df_sub[pct_change].iloc[i] > 0:

                higher_values = df_sub[df_sub[field] > df_sub[field].iloc[i]]

                previous_higher_values = higher_values[higher_values['auction_date'] < df_sub['auction_date'].iloc[i]]
                    
                if not previous_higher_values.empty:
                    df_sub[days_since].iloc[i] = (df_sub['auction_date'].iloc[i] - previous_higher_values['auction_date'].iloc[-1]).days
        
        inner(field='bid_to_cover_ratio',       pct_change='bid_to_cover_ratio_pct_change',       days_since='bid_to_cover_ratio_days')
        inner(field='direct_bidder_accepted',   pct_change='direct_bidder_accepted_pct_change',   days_since='direct_bidder_accepted_days')
        inner(field='indirect_bidder_accepted', pct_change='indirect_bidder_accepted_pct_change', days_since='indirect_bidder_accepted_days')

    return df_sub

# ----------------------------------------------------------------------


# show_concise_alt(df_30_year.tail(20))

# ----------------------------------------------------------------------

# df_in = df_30_year

def show_concise_alt_formatted(df_in):

    df_in['btc_pct']      = (df_in['bid_to_cover_ratio_pct_change']      *100).round(2)
    df_in['direct_pct']   = (df_in['direct_bidder_accepted_pct_change']  *100).round(2)
    df_in['indirect_pct'] = (df_in['indirect_bidder_accepted_pct_change']*100).round(2)
    
    df_in['btc_days']      = df_in['bid_to_cover_ratio_days'].astype('Int64')
    df_in['direct_days']   = df_in['direct_bidder_accepted_days'].astype('Int64')
    df_in['indirect_days'] = df_in['indirect_bidder_accepted_days'].astype('Int64')

    df_in['direct_pct_of_comp']   = (df_in['direct_pct_of_competitive']*100).round(2)
    df_in['indirect_pct_of_comp'] = (df_in['indirect_pct_of_competitive']*100).round(2)
   
    print(
        df_in
            .sort_values(by=['auction_date'])
            .rename(columns={
                'bid_to_cover_ratio': 'btc',
                'direct_bidder_accepted': 'direct',
                'indirect_bidder_accepted': 'indirect',
                # 'direct_bidder_accepted_days': 'direct_days',
                # 'indirect_bidder_accepted_days': 'indirect_days'
                })
            [[
                'auction_date', 'security_type', 'security_term', 'original_security_term',
                'btc',      'btc_pct',      'btc_days',
                'direct',   'direct_pct',   'direct_days', 
                'indirect', 'indirect_pct', 'indirect_days',
                'direct_pct_of_comp', 'indirect_pct_of_comp'
            ]].to_string())

# df_10_year = auction_table('10-Year', tips='No')

# show_concise_alt_formatted(df_10_year.tail(40))


# df_20_year = auction_table('20-Year', tips='No')

# show_concise_alt_formatted(df_20_year.tail(40))


# df_30_year = auction_table('30-Year', tips='No')

# show_concise_alt_formatted(df_30_year.tail(40))
