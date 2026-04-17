import pandas as pd
import os
import datetime
import re

def dataset_clean():
    #Select Directory Dataset
    base_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(base_dir,'..', 'dataset')
    
    #Load Dataset Principal and Libray Publishers and Developers
    df = pd.read_csv(os.path.join(dataset_dir, 'video_game_sales.csv'))
    df_catch_pubs_devs = pd.read_csv(os.path.join(dataset_dir, 'dataset_limpeza.csv'), sep=';')
    df1 = df.copy()
    
    #1. Creating the name_console; manufacture; generation, plataform and cycle life
    console_name = {'PS3' : 'Playstation 3', 'PS4' : 'Playstation 4', 'PS2' : 'Playstation 2', 'X360' : 'Xbox 360', 'XOne' : 'Xbox One',
                'PC' : 'PC', 'PSP' : 'PSP', 'Wii' : 'Nintendo Wii', 'PS' : 'PlayStation', 'DS' : 'Nintendo DS', '2600' : 'Atari 2600', 
                'GBA' : 'GameBoy Advanced', 'NES': 'NES', 'XB' : 'Xbox', 'PSN' : 'Playstation Digital', 'GEN' : 'Sega Genesis', 
                'PSV' : 'PSVita', 'DC' : 'Sega DreamCast', 'N64' : 'Nintendo 64', 'SAT' : 'Sega Saturn', 'SNES' : 'Super Nintendo', 
                'GBC' : 'GameBoy Color', 'GC' : 'Nintendo GameCube', 'NS' : 'Nintendo Switch', '3DS': 'Nintendo 3DS', 
                'GB': 'Nintendo GameBoy', 'WiiU' : 'Nintendo WiiU', 'WS' : 'WonderSwan', 'VC' : 'Virtual Console Digital', 'NG':'NeoGeo', 
                'WW' : 'WiiWare Digital', 'SCD': 'Sega CD', 'PCE' : 'PC Engine', 'XBL': 'Xbox Live Digital', '3DO' : '3DO', 
                'GG' : 'Sega GameGear', 'OSX' : 'Apple PC OSX', 'Mob' : 'Mobile', 'PCFX' : 'PCFX', 'Series' : 'Xbox Series', 'All' : 'All', 
                'iOS': 'Apple iOS', '5200' :  'Atari 5200', 'And' : 'Android', 'DSiW': 'Nintendo DSi Digital', 'Lynx' : 'Atari Lynx',
                'Linux': 'Linux PC', 'MS' : 'Sega MasterSystem', 'ZXS' : 'ZX Spectrum', 'ACPC' : 'Amstrad CPC', 'Amig': 'Commodore Amiga',
                '7800' : 'Atari 7800', 'DSi' : 'Nintendo DS', 'AJ': 'Atari Jaguar', 'WinP': 'Windows Phone', 'iQue' : 'iQue Player',
                'GIZ': 'Gizmondo', 'VB': 'Nintendo VirtualBoy', 'Ouya': 'Ouya', 'NGage': 'Nokia NGage', 'AST': 'Atari ST PC', 'MSD':'MS-DOS',
                'S32X': 'Sega 32X', 'XS' : 'Xbox Series', 'PS5' : 'Playstation 5', 'Int': 'Intellivision', 'CV': 'ColecoVision', 
                'Arc': 'Arcade', 'C64': 'Commodore 64', 'FDS' : 'NES', 'MSX' : 'MSX', 'OR' : 'Oculus Rift', 'C128' : 'Commodore 128',
                'CDi': 'Philips CD Interactive', 'CD32' : 'Amiga CD32', 'BRW' : 'Web Browser Games', 'FMT' : 'FM Towns', 'ApII' : 'PC Apple II',
                'Aco': 'Acorn Archimedes', 'BBCM' : 'BBC Micro', 'TG16': 'PC Engine'}

    df1['console_name'] = df['console'].map(console_name).fillna('Other/Unknown')
    
    manufacture = {
    # Sony
    'PS': 'Sony', 'PS1': 'Sony', 'PS2': 'Sony', 'PS3': 'Sony', 'PS4': 'Sony', 'PS5': 'Sony', 
    'PSP': 'Sony', 'PSV': 'Sony', 'PSX': 'Sony', 'PSN': 'Sony',
    
    # Nintendo
    'NES': 'Nintendo', 'SNES': 'Nintendo', 'N64': 'Nintendo', 'GC': 'Nintendo', 'Wii': 'Nintendo', 
    'WiiU': 'Nintendo', 'Switch': 'Nintendo', 'NS': 'Nintendo', 'GB': 'Nintendo', 'GBA': 'Nintendo', 
    'GBC': 'Nintendo', 'DS': 'Nintendo', 'DSi': 'Nintendo', '3DS': 'Nintendo', 'VB': 'Nintendo', 
    'iQue': 'Nintendo', 'FDS': 'Nintendo', 'VC': 'Nintendo', 'DSiW': 'Nintendo',
    
    # Microsoft / PC
    'XB': 'Microsoft', 'X360': 'Microsoft', 'XOne': 'Microsoft', 'XS': 'Microsoft', 
    'XSX': 'Microsoft', 'XSS': 'Microsoft', 'Series': 'Microsoft', 'MSD': 'Microsoft', 
    'WinP': 'Microsoft', 'PC': 'PC/Other', 'Win': 'PC/Other', 'OSX': 'Apple', 'ApII': 'Apple', 
    
    # Sega
    'MS': 'Sega', 'GEN': 'Sega', 'MD': 'Sega', 'SAT': 'Sega', 'DC': 'Sega', 
    'GG': 'Sega', 'SCD': 'Sega', 'S32X': 'Sega',
    
    # Atari
    '2600': 'Atari', '5200': 'Atari', '7800': 'Atari', 'AJ': 'Atari', 'Lynx': 'Atari', 'AST': 'Atari',
    
    # Commodore
    'C64': 'Commodore', 'C128': 'Commodore', 'Amig': 'Commodore', 'CD32': 'Commodore', 'VIC20': 'Commodore',
    
    # Outros
    'PCE': 'NEC', 'TG16': 'NEC', 'PCFX': 'NEC', 'WS': 'Bandai', 'WSC': 'Bandai',
    '3DO': 'Panasonic', 'CDi': 'Philips', 'Int': 'Mattel', 'CV': 'Coleco',
    'FMT': 'Fujitsu', 'Aco': 'Acorn', 'BBCM': 'Acorn', 'GIZ': 'Tiger', 'Ouya': 'Ouya',
    'Arc': 'Arcade', 'Mob': 'Mobile', 'And': 'Mobile', 'iOS': 'Mobile', 'BRW': 'Web',
    'OR': 'Oculus/Meta', 'NG': 'SNK', 'NEO': 'SNK', 'NGP': 'SNK'
}

    df1['manufacture'] = df['console'].map(manufacture).fillna('Other/Unknown')
    
    gen_mapping = {
    '2600': '2nd Gen', '5200': '2nd Gen', 'Int': '2nd Gen', 'CV': '2nd Gen', 
    'NES': '3rd Gen', 'MS': '3rd Gen', '7800': '3rd Gen', 'GG': '3rd Gen', 'FDS': '3rd Gen', 'MSX': '3rd Gen',
    'SNES': '4th Gen', 'GEN': '4th Gen', 'MD': '4th Gen', 'GB': '4th Gen', 'TG16': '4th Gen', 'NG': '4th Gen', 'SCD': '4th Gen',
    'PCE': '4th Gen', 'Lynx': '4th Gen', 'S32X': '4th Gen',
    'PS': '5th Gen', 'PS1': '5th Gen', 'N64': '5th Gen', 'SAT': '5th Gen', 'AJ': '5th Gen', 'GBC': '5th Gen', '3DO': '5th Gen',
    'PCFX': '5th Gen', 'VB': '5th Gen',
    'PS2': '6th Gen', 'XB': '6th Gen', 'GC': '6th Gen', 'DC': '6th Gen', 'GBA': '6th Gen', 'WS': '6th Gen', 'iQue': '6th Gen',
    'NGage': '6th Gen',
    'PS3': '7th Gen', 'X360': '7th Gen', 'Wii': '7th Gen', 'DS': '7th Gen', 'PSP': '7th Gen', 'DSi': '7th Gen', 'GIZ': '7th Gen',
    'PS4': '8th Gen', 'XOne': '8th Gen', 'WiiU': '8th Gen', 'NS': '8th Gen', '3DS': '8th Gen', 'PSV': '8th Gen', 'Ouya': '8th Gen',
    'PS5': '9th Gen', 'XS': '9th Gen', 'Series': '9th Gen'
    }
    
    df1['generation'] = df['console'].map(gen_mapping).fillna('Other/Unknown')
    
    plataform = {
    #PC
    'PC': 'PC', 'OSX': 'PC', 'Linux': 'PC', 'ZXS': 'PC', 'ACPC': 'PC', 'Amig': 'PC', 
    'AST': 'PC', 'MSX': 'PC', 'C64': 'PC', 'C128':'PC', 'FMT': 'PC', 'ApII': 'PC', 'Aco' :'PC', 'BBCM': 'PC',
    #Mobile
    'Mob': 'Mobile', 'iOS': 'Mobile', 'And': 'Mobile', 'WinP': 'Mobile',
    #Digital Service
   'PSN' : 'Digital Service', 'XBL': 'Digital Service', 'VC' : 'Digital Service', 'WW' : 'Digital Service', 
   'DSiW' : 'Digital Service', 'BRW':'Digital Service'
    }

    df1['plataform'] = df1['console'].map(plataform).fillna('Console')
    
    portable = {
    'PSP': 'Yes', 'DS': 'Yes', 'DSi': 'Yes', 'GBA': 'Yes', 'PSV': 'Yes', 'GBC': 'Yes', 'NS': 'Yes',
    '3DS': 'Yes', 'GB': 'Yes', 'WS': 'Yes', 'GG': 'Yes', 'Lynx': 'Yes', 'GIZ': 'Yes', 'VB' : 'Yes'
    }
    
    df1['portable'] = df1['console'].map(portable).fillna('No')
    
    actual_year = 2026
    consoles_cycle_life = {
    'PS3': [2006, 2017], 'PS4': [2013, None], 'PS2': [2000, 2013], 
    'X360': [2005, 2016], 'XOne': [2013, None], 'PC': [1985, None], 
    'PSP': [2004, 2014], 'Wii': [2006, 2013], 'PS': [1994, 2004], 
    'DS': [2004, 2013], '2600': [1977, 1992], 'GBA': [2001, 2008], 
    'NES': [1983, 1995], 'XB': [2001, 2009], 'PSN': [2006, None], 
    'GEN': [1988, 1998], 'PSV': [2011, 2019], 'DC': [1998, 2001], 
    'N64': [1996, 2002], 'SAT': [1994, 2000], 'SNES': [1990, 2003], 
    'GBC': [1998, 2003], 'GC': [2001, 2007], 'NS': [2017, None], 
    '3DS': [2011, 2020], 'GB': [1989, 2003], 'WiiU': [2012, 2017], 
    'WS': [1999, 2003], 'VC': [2006, 2019], 'NG': [1990, 2004], 
    'WW': [2008, 2019], 'SCD': [1991, 1996], 'PCE': [1987, 1994], 
    'XBL': [2002, None], '3DO': [1993, 1996], 'GG': [1990, 1997], 
    'OSX': [2001, None], 'Mob': [2008, None], 'PCFX': [1994, 1998], 
    'Series': [2020, None], 'iOS': [2008, None], '5200': [1982, 1984], 
    'And': [2008, None], 'DSiW': [2008, 2017], 'Lynx': [1989, 1995], 
    'Linux': [1991, None], 'MS': [1985, 1992], 'ZXS': [1982, 1992], 
    'ACPC': [1984, 1990], 'Amig': [1985, 1996], '7800': [1986, 1991], 
    'DSi': [2008, 2013], 'AJ': [1993, 1996], 'WinP': [2010, 2019], 
    'iQue': [2003, 2018], 'GIZ': [2005, 2006], 'VB': [1995, 1996], 
    'Ouya': [2013, 2015], 'NGage': [2003, 2005], 'AST': [1985, 1993], 
    'MSD': [1981, 2000], 'S32X': [1994, 1996], 'XS': [2020, None], 
    'PS5': [2020, None], 'Int': [1979, 1991], 'CV': [1982, 1985], 
    'Arc': [1971, None], 'C64': [1982, 1994], 'FDS': [1986, 2003], 
    'MSX': [1983, 1995], 'OR': [2016, None], 'C128': [1985, 1989], 
    'CDi': [1991, 1998], 'CD32': [1993, 1994], 'BRW': [1995, None], 
    'FMT': [1989, 1997], 'ApII': [1977, 1993], 'Aco': [1987, 1992], 
    'BBCM': [1981, 1994], 'TG16': [1987, 1994]
    }

    df_ref = pd.DataFrame.from_dict(consoles_cycle_life, orient = 'index', columns = ['start_year', 'end_year'])
    df_ref['end_year'] = df_ref['end_year'].fillna(actual_year)
    df_ref['activity_years'] = df_ref['end_year'] - df_ref['start_year']
    df_ref['activity_years'] = df_ref['activity_years'].replace(0,1)
    
    df1 = df1.merge(df_ref[['start_year','end_year','activity_years',]], left_on = 'console', right_index=True, how='left')
    
    #2.Merge links (domain + url chart game)
    domain = "https://vgchartz.com"
    df1['url_chart'] = domain + df1['img']
    
    #3. Format date
    df1['release_date'] = pd.to_datetime(df['release_date'])
    
    #4.Verification the space before or after the sentence
    for col in df1.select_dtypes(include='object').columns:
        try:
            df1[col] = df1[col].str.strip()
        except AttributeError:
            pass
    
    #6.Insert qualify column into dataset
    df1['classification'] = pd.cut(
        df1['critic_score'],
        bins=[-float('inf'), 5.0, 7.0, 9.0, float('inf')],
        labels=['Bad', 'Regular', 'Good', 'Premium']
    ).cat.add_categories('Unrated').fillna('Unrated')
    
    #7. Merge Country and Corret Names -> Dataset_Limpeza.csv

    map_country_studios = df_catch_pubs_devs.set_index('original_term')['studio_location']
    map_dev_pub = df_catch_pubs_devs.set_index('original_term')['clean_name']
    map_holdings = df_catch_pubs_devs.set_index('original_term')['holding']

    df1['country_publisher'] = df1['publisher'].map(map_country_studios)
    df1['clean_name_publisher'] = df1['publisher'].map(map_dev_pub)
    df1['holdings_publisher'] = df1['publisher'].map(map_holdings)

    df1['country_developer'] = df1['developer'].map(map_country_studios)
    df1['clean_name_developer'] = df1['developer'].map(map_dev_pub)
    df1['holdings_developer'] = df1['publisher'].map(map_holdings)
    
    #8.Holdings Country
    df_map_holdings = df_catch_pubs_devs.drop_duplicates(subset='holding', keep='first')
    map_country_holdings = df_map_holdings.set_index('holding')['country_origin']
    
    df1['holdings_publisher_country'] = df1['holdings_publisher'].map(map_country_holdings)
    
    #9.Drop img column
    df1 = df1.drop('img', axis = 1)
    
    return df1