import pandas as pd
import os
import datetime
import re
import streamlit as st
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# Constantes — definidas uma única vez no módulo, não recriadas a cada chamada
# ══════════════════════════════════════════════════════════════════════════════

_CONSOLE_NAME = {
    'PS3': 'Playstation 3', 'PS4': 'Playstation 4', 'PS2': 'Playstation 2',
    'X360': 'Xbox 360', 'XOne': 'Xbox One', 'PC': 'PC', 'PSP': 'PSP',
    'Wii': 'Nintendo Wii', 'PS': 'PlayStation', 'DS': 'Nintendo DS',
    '2600': 'Atari 2600', 'GBA': 'GameBoy Advanced', 'NES': 'NES',
    'XB': 'Xbox', 'PSN': 'Playstation Digital', 'GEN': 'Sega Genesis',
    'PSV': 'PSVita', 'DC': 'Sega DreamCast', 'N64': 'Nintendo 64',
    'SAT': 'Sega Saturn', 'SNES': 'Super Nintendo', 'GBC': 'GameBoy Color',
    'GC': 'Nintendo GameCube', 'NS': 'Nintendo Switch', '3DS': 'Nintendo 3DS',
    'GB': 'Nintendo GameBoy', 'WiiU': 'Nintendo WiiU', 'WS': 'WonderSwan',
    'VC': 'Virtual Console Digital', 'NG': 'NeoGeo', 'WW': 'WiiWare Digital',
    'SCD': 'Sega CD', 'PCE': 'PC Engine', 'XBL': 'Xbox Live Digital',
    '3DO': '3DO', 'GG': 'Sega GameGear', 'OSX': 'Apple PC OSX',
    'Mob': 'Mobile', 'PCFX': 'PCFX', 'Series': 'Xbox Series', 'All': 'All',
    'iOS': 'Apple iOS', '5200': 'Atari 5200', 'And': 'Android',
    'DSiW': 'Nintendo DSi Digital', 'Lynx': 'Atari Lynx', 'Linux': 'Linux PC',
    'MS': 'Sega MasterSystem', 'ZXS': 'ZX Spectrum', 'ACPC': 'Amstrad CPC',
    'Amig': 'Commodore Amiga', '7800': 'Atari 7800', 'DSi': 'Nintendo DS',
    'AJ': 'Atari Jaguar', 'WinP': 'Windows Phone', 'iQue': 'iQue Player',
    'GIZ': 'Gizmondo', 'VB': 'Nintendo VirtualBoy', 'Ouya': 'Ouya',
    'NGage': 'Nokia NGage', 'AST': 'Atari ST PC', 'MSD': 'MS-DOS',
    'S32X': 'Sega 32X', 'XS': 'Xbox Series', 'PS5': 'Playstation 5',
    'Int': 'Intellivision', 'CV': 'ColecoVision', 'Arc': 'Arcade',
    'C64': 'Commodore 64', 'FDS': 'NES', 'MSX': 'MSX', 'OR': 'Oculus Rift',
    'C128': 'Commodore 128', 'CDi': 'Philips CD Interactive',
    'CD32': 'Amiga CD32', 'BRW': 'Web Browser Games', 'FMT': 'FM Towns',
    'ApII': 'PC Apple II', 'Aco': 'Acorn Archimedes', 'BBCM': 'BBC Micro',
    'TG16': 'PC Engine',
}

_MANUFACTURE = {
    'PS': 'Sony', 'PS1': 'Sony', 'PS2': 'Sony', 'PS3': 'Sony', 'PS4': 'Sony',
    'PS5': 'Sony', 'PSP': 'Sony', 'PSV': 'Sony', 'PSX': 'Sony', 'PSN': 'Sony',
    'NES': 'Nintendo', 'SNES': 'Nintendo', 'N64': 'Nintendo', 'GC': 'Nintendo',
    'Wii': 'Nintendo', 'WiiU': 'Nintendo', 'Switch': 'Nintendo', 'NS': 'Nintendo',
    'GB': 'Nintendo', 'GBA': 'Nintendo', 'GBC': 'Nintendo', 'DS': 'Nintendo',
    'DSi': 'Nintendo', '3DS': 'Nintendo', 'VB': 'Nintendo', 'iQue': 'Nintendo',
    'FDS': 'Nintendo', 'VC': 'Nintendo', 'DSiW': 'Nintendo',
    'XB': 'Microsoft', 'X360': 'Microsoft', 'XOne': 'Microsoft', 'XS': 'Microsoft',
    'XSX': 'Microsoft', 'XSS': 'Microsoft', 'Series': 'Microsoft', 'MSD': 'Microsoft',
    'WinP': 'Microsoft', 'PC': 'PC/Other', 'Win': 'PC/Other', 'OSX': 'Apple', 'ApII': 'Apple',
    'MS': 'Sega', 'GEN': 'Sega', 'MD': 'Sega', 'SAT': 'Sega', 'DC': 'Sega',
    'GG': 'Sega', 'SCD': 'Sega', 'S32X': 'Sega',
    '2600': 'Atari', '5200': 'Atari', '7800': 'Atari', 'AJ': 'Atari',
    'Lynx': 'Atari', 'AST': 'Atari',
    'C64': 'Commodore', 'C128': 'Commodore', 'Amig': 'Commodore',
    'CD32': 'Commodore', 'VIC20': 'Commodore',
    'PCE': 'NEC', 'TG16': 'NEC', 'PCFX': 'NEC',
    'WS': 'Bandai', 'WSC': 'Bandai',
    '3DO': 'Panasonic', 'CDi': 'Philips', 'Int': 'Mattel', 'CV': 'Coleco',
    'FMT': 'Fujitsu', 'Aco': 'Acorn', 'BBCM': 'Acorn', 'GIZ': 'Tiger',
    'Ouya': 'Ouya', 'Arc': 'Arcade', 'Mob': 'Mobile', 'And': 'Mobile',
    'iOS': 'Mobile', 'BRW': 'Web', 'OR': 'Oculus/Meta', 'NG': 'SNK',
    'NEO': 'SNK', 'NGP': 'SNK',
}

_GEN_MAPPING = {
    '2600': '2nd Gen', '5200': '2nd Gen', 'Int': '2nd Gen', 'CV': '2nd Gen',
    'NES': '3rd Gen', 'MS': '3rd Gen', '7800': '3rd Gen', 'GG': '3rd Gen',
    'FDS': '3rd Gen', 'MSX': '3rd Gen',
    'SNES': '4th Gen', 'GEN': '4th Gen', 'MD': '4th Gen', 'GB': '4th Gen',
    'TG16': '4th Gen', 'NG': '4th Gen', 'SCD': '4th Gen', 'PCE': '4th Gen',
    'Lynx': '4th Gen', 'S32X': '4th Gen',
    'PS': '5th Gen', 'PS1': '5th Gen', 'N64': '5th Gen', 'SAT': '5th Gen',
    'AJ': '5th Gen', 'GBC': '5th Gen', '3DO': '5th Gen', 'PCFX': '5th Gen',
    'VB': '5th Gen',
    'PS2': '6th Gen', 'XB': '6th Gen', 'GC': '6th Gen', 'DC': '6th Gen',
    'GBA': '6th Gen', 'WS': '6th Gen', 'iQue': '6th Gen', 'NGage': '6th Gen',
    'PS3': '7th Gen', 'X360': '7th Gen', 'Wii': '7th Gen', 'DS': '7th Gen',
    'PSP': '7th Gen', 'DSi': '7th Gen', 'GIZ': '7th Gen',
    'PS4': '8th Gen', 'XOne': '8th Gen', 'WiiU': '8th Gen', 'NS': '8th Gen',
    '3DS': '8th Gen', 'PSV': '8th Gen', 'Ouya': '8th Gen',
    'PS5': '9th Gen', 'XS': '9th Gen', 'Series': '9th Gen',
}

_PLATAFORM = {
    'PC': 'PC', 'OSX': 'PC', 'Linux': 'PC', 'ZXS': 'PC', 'ACPC': 'PC',
    'Amig': 'PC', 'AST': 'PC', 'MSX': 'PC', 'C64': 'PC', 'C128': 'PC',
    'FMT': 'PC', 'ApII': 'PC', 'Aco': 'PC', 'BBCM': 'PC',
    'Mob': 'Mobile', 'iOS': 'Mobile', 'And': 'Mobile', 'WinP': 'Mobile',
    'PSN': 'Digital Service', 'XBL': 'Digital Service', 'VC': 'Digital Service',
    'WW': 'Digital Service', 'DSiW': 'Digital Service', 'BRW': 'Digital Service',
}

_PORTABLE = {
    'PSP', 'DS', 'DSi', 'GBA', 'PSV', 'GBC', 'NS',
    '3DS', 'GB', 'WS', 'GG', 'Lynx', 'GIZ', 'VB',
}

_CONSOLES_CYCLE_LIFE = {
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
    'BBCM': [1981, 1994], 'TG16': [1987, 1994],
}

_PLATFORM_LAUNCH = {
    'PS': '1994-12-03', 'PS2': '2000-03-04', 'PS3': '2006-11-11',
    'PS4': '2013-11-15', 'PS5': '2020-11-12', 'PSP': '2004-12-12',
    'PSV': '2011-12-17', 'PSN': '2006-11-11',
    'XB': '2001-11-15', 'X360': '2005-11-22', 'XOne': '2013-11-22',
    'XS': '2020-11-10', 'XBL': '2002-11-15',
    'NES': '1983-07-15', 'SNES': '1990-11-21', 'N64': '1996-06-23',
    'GC': '2001-09-14', 'Wii': '2006-11-19', 'WiiU': '2012-11-18',
    'NS': '2017-03-03', 'GB': '1989-04-21', 'GBC': '1998-10-21',
    'GBA': '2001-03-21', 'DS': '2004-11-21', '3DS': '2011-02-26',
    'VB': '1995-07-21', 'FDS': '1986-02-21',
    'GEN': '1988-10-29', 'SAT': '1994-11-22', 'DC': '1998-11-27',
    'SCD': '1991-12-12', 'S32X': '1994-11-21', 'GG': '1990-10-06',
    'MS': '1985-10-20',
    '2600': '1977-09-11', '5200': '1982-11-01', '7800': '1986-05-01',
    'Lynx': '1989-09-01', 'AST': '1985-01-01',
    'PCE': '1987-10-30', 'TG16': '1989-08-29',
    'NG': '1990-04-26', 'NGage': '2003-10-07',
    '3DO': '1993-10-04', 'WS': '1999-03-04', 'WW': '2000-12-09',
    'PC': '1981-01-01', 'OSX': '2001-03-24', 'Linux': '1991-09-17',
    'Mob': '2000-01-01', 'iOS': '2008-07-10', 'And': '2008-10-22',
    'CDi': '1991-12-03', 'C64': '1982-08-01', 'C128': '1985-01-01',
    'Amig': '1985-07-23', 'CD32': '1993-09-17', 'ZXS': '1982-04-23',
    'ACPC': '1984-06-01', 'MSX': '1983-06-16', 'PCFX': '1994-12-23',
    'FMT': '1989-01-01', 'ApII': '1977-06-05', 'BBCM': '1981-12-01',
    'CV': '1982-08-01', 'Int': '1979-01-01', 'Arc': '1987-06-24',
    'Aco': '1987-06-24', 'iQue': '2003-11-17', 'DSiW': '2008-11-01',
    'DSi': '2008-11-01', 'VC': '2006-11-19', 'WinP': '2010-10-21',
    'Ouya': '2013-06-25', 'OR': '2016-03-28', 'GIZ': '2013-04-01',
    'MSD': '1983-01-01', 'AJ': '1990-01-01', 'BRW': '1990-01-01',
    'Series': '2020-11-10',
}

_STR_CLEAN_PATTERN = re.compile(r'[^\w\s\-\:\.\!\?\&\'\,]')
_WHITESPACE_PATTERN = re.compile(r'\s+')

# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def dataset_clean():
    """
    Carrega e enriquece o dataset de vendas de jogos (video_game_sales.csv),
    retornando um DataFrame limpo e pronto para análise.

    Etapas aplicadas
    ----------------
    1. Mapeamento de console → nome legível, fabricante, geração, plataforma
       e portabilidade a partir de dicionários de referência.
    2. Merge com ciclo de vida dos consoles (start_year, end_year,
       activity_years).
    3. Merge com data de lançamento de cada console
       (release_date_console).
    4. Construção da URL de capa: domínio vgchartz.com + coluna img.
    5. Conversão de release_date para datetime.
    6. Criação da coluna classification com base no critic_score:
       Bad (≤5), Regular (5-7), Good (7-9), Premium (>9), Unrated (sem nota).
    7. Merge com dataset_limpeza.csv para obter:
       - country_publisher / country_developer
       - clean_name_publisher / clean_name_developer
       - holdings_publisher / holdings_developer
       - holdings_publisher_country
    8. Limpeza de strings em todas as colunas de texto:
       strip, colapso de espaços múltiplos, remoção de caracteres especiais
       e normalização Unicode NFC.

    Parâmetros
    ----------
    Nenhum — caminhos são resolvidos relativamente ao arquivo data_loader.py.

    Retorna
    -------
    df1 : pd.DataFrame
        Dataset enriquecido com todas as colunas adicionais descritas acima.
        Resultado em cache pelo Streamlit (@st.cache_data).

    Colunas adicionadas
    -------------------
    console_name             : str   — nome completo do console
    manufacture              : str   — fabricante (Sony, Nintendo, Microsoft…)
    generation               : str   — geração do console (2nd Gen … 9th Gen)
    plataform                : str   — Console | PC | Mobile | Digital Service
    portable                 : str   — Yes | No
    start_year               : int   — ano de início do console
    end_year                 : int   — ano de fim (2026 se ainda ativo)
    activity_years           : int   — anos de atividade do console
    release_date_console     : datetime — data de lançamento do console
    url_chart                : str   — URL da capa em vgchartz.com
    release_date             : datetime — data de lançamento do jogo
    classification           : str   — Bad | Regular | Good | Premium | Unrated
    country_publisher        : str   — país da publisher
    clean_name_publisher     : str   — nome limpo da publisher
    holdings_publisher       : str   — holding da publisher
    country_developer        : str   — país da desenvolvedora
    clean_name_developer     : str   — nome limpo da desenvolvedora
    holdings_developer       : str   — holding da desenvolvedora
    holdings_publisher_country: str  — país de origem da holding
    """

    # ── Paths ─────────────────────────────────────────────────────────────────
    base_dir    = Path(__file__).parent
    dataset_dir = base_dir / '..' / 'assets' / 'data'

    # ── Carregamento ──────────────────────────────────────────────────────────
    df  = pd.read_csv(dataset_dir / 'video_game_sales.csv')
    df_catch_pubs_devs = pd.read_csv(dataset_dir / 'dataset_limpeza.csv', sep=';')
    df1 = df.copy()

    # ── 1. Colunas derivadas do console ───────────────────────────────────────
    console = df1['console']
    df1['console_name'] = console.map(_CONSOLE_NAME).fillna('Other/Unknown')
    df1['manufacture']  = console.map(_MANUFACTURE).fillna('Other/Unknown')
    df1['generation']   = console.map(_GEN_MAPPING).fillna('Other/Unknown')
    df1['plataform']    = console.map(_PLATAFORM).fillna('Console')
    df1['portable']     = console.map(lambda c: 'Yes' if c in _PORTABLE else 'No')

    # ── 2. Ciclo de vida dos consoles ─────────────────────────────────────────
    ACTUAL_YEAR = 2026
    df_ref = (
        pd.DataFrame.from_dict(_CONSOLES_CYCLE_LIFE, orient='index', columns=['start_year', 'end_year'])
        .assign(end_year=lambda d: d['end_year'].fillna(ACTUAL_YEAR))
    )
    df_ref['activity_years'] = (df_ref['end_year'] - df_ref['start_year']).replace(0, 1)

    df1 = df1.merge(
        df_ref[['start_year', 'end_year', 'activity_years']],
        left_on='console', right_index=True, how='left',
    )

    # ── 3. Data de lançamento dos consoles ────────────────────────────────────
    df_platform_launch = (
        pd.DataFrame.from_dict(_PLATFORM_LAUNCH, orient='index', columns=['release_date_console'])
        .dropna()
    )
    df_platform_launch['release_date_console'] = pd.to_datetime(df_platform_launch['release_date_console'])

    df1 = df1.merge(df_platform_launch, left_on='console', right_index=True, how='left')

    # ── 4. URL de capa ────────────────────────────────────────────────────────
    df1['url_chart'] = 'https://vgchartz.com' + df1['img']

    # ── 5. Data de lançamento do jogo ─────────────────────────────────────────
    df1['release_date'] = pd.to_datetime(df['release_date'])

    # ── 6. Classificação por critic_score ─────────────────────────────────────
    df1['classification'] = (
        pd.cut(
            df1['critic_score'],
            bins=[-float('inf'), 5.0, 7.0, 9.0, float('inf')],
            labels=['Bad', 'Regular', 'Good', 'Premium'],
        )
        .cat.add_categories('Unrated')
        .fillna('Unrated')
    )

    # ── 7. Merge com dataset_limpeza ──────────────────────────────────────────
    idx = df_catch_pubs_devs.set_index('original_term')

    df1['country_publisher']    = df1['publisher'].map(idx['studio_location'])
    df1['clean_name_publisher'] = df1['publisher'].map(idx['clean_name'])
    df1['holdings_publisher']   = df1['publisher'].map(idx['holding'])

    df1['country_developer']    = df1['developer'].map(idx['studio_location'])
    df1['clean_name_developer'] = df1['developer'].map(idx['clean_name'])
    df1['holdings_developer']   = df1['publisher'].map(idx['holding'])

    df_map_holdings = df_catch_pubs_devs.drop_duplicates(subset='holding', keep='first')
    df1['holdings_publisher_country'] = df1['holdings_publisher'].map(
        df_map_holdings.set_index('holding')['country_origin']
    )

    # ── 8. Limpeza de strings ─────────────────────────────────────────────────
    for col in df1.select_dtypes(include='object').columns:
        try:
            df1[col] = (
                df1[col]
                .str.strip()
                .str.replace(_WHITESPACE_PATTERN, ' ', regex=True)
                .str.replace(_STR_CLEAN_PATTERN,  '', regex=True)
                .str.normalize('NFC')
            )
        except AttributeError:
            pass

    # ── 9. Remove coluna auxiliar ─────────────────────────────────────────────
    df1 = df1.drop(columns='img')

    return df1