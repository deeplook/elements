#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Playing with the elements...

>>> from elements import *
>>> url = "https://en.wikipedia.org/w/index.php?title=Template:Infobox_titanium&action=edit"
>>> ib = get_infobox_text(url)
>>> ti = infobox2dict(ib)
No handlers could be found for logger "root"
>>> ti['symbol']
u'Ti'
>>> ti['number']
u'22'
>>> ti['melting point C']
u'1668'
>>> ti['density gpcm3nrt']
u'4.506'
"""

import re
import os
import sys
import json
import argparse
import HTMLParser

import requests
import tabulate
import pandas as pd
from mwtemplates import TemplateEditor


def get_infobox_text(url):
    "Get Wikipedia Infobox as raw HTML text (Unicode)."

    resp = requests.get(url)
    html = resp.content
    res = None
    m = re.search('<textarea.*?>({{.*}}).*</textarea>', html, re.S)
    if m:
        infobox = m.groups()[0]
        res = infobox
    return res.decode('utf-8')


def infobox2dict(txt):
    "Convert some raw Infobox Unicode text to a Python dict-like object."

    pars = HTMLParser.HTMLParser()
    txt = pars.unescape(txt)

    te = TemplateEditor(txt)
    ie = te.templates['Infobox element']
    ie0 = ie[0]
    # ie0.parameters['symbol'] # 'Ti'
    # ie0.parameters['appearance'] # 'silvery grey-white metallic'
    # ie0.parameters['melting point C'] # 1668
    # params = ie0.parameters # needs UTF-8
    # res = params.items() # [(Unicode key, mwtemplates object)]
    res = [(k, str(ie0.parameters[k]).decode('utf-8')) for k in ie0.parameters.keys()]
    res = dict(res)
    return res


def test():
    url = "https://en.wikipedia.org/w/index.php?title=Template:Infobox_titanium&action=edit"
    ib = get_infobox_text(url)
    # print infobox2dict(txt)
    params = infobox2dict(infobox_sample_short_ok)
    d = dict(params.items())
    print d


def test_unicode():
    "Short test for prooving existing Unicode issues."
    
    from mwtemplates import TemplateEditor
    wikitext = u"{{ infobox element |number=22 |name=titanium }}"
    wikitext = u"{{ infobox element |number=22 |name=Jöns }}" # UnicodeEncodeError
    te = TemplateEditor(wikitext.encode('utf-8'))
    ie = te.templates['Infobox element']
    print ie[0].parameters


element_names = 'Actinium Aluminium Americium Antimony Argon Arsenic Astatine Barium Berkelium Beryllium Bismuth Bohrium Boron Bromine Cadmium Caesium Calcium Californium Carbon Cerium Chlorine Chromium Cobalt Copernicium Copper Curium Darmstadtium Dubnium Dysprosium Einsteinium Erbium Europium Fermium Flerovium Fluorine Francium Gadolinium Gallium Germanium Gold Hafnium Hassium Helium Holmium Hydrogen Indium Iodine Iridium Iron Krypton Lanthanum Lawrencium Lead Lithium Livermorium Lutetium Magnesium Manganese Meitnerium Mendelevium Mercury Molybdenum Neodymium Neon Neptunium Nickel Niobium Nitrogen Nobelium Osmium Oxygen Palladium Phosphorus Platinum Plutonium Polonium Potassium Praseodymium Promethium Protactinium Radium Radon Rhenium Rhodium Roentgenium Rubidium Ruthenium Rutherfordium Samarium Scandium Seaborgium Selenium Silicon Silver Sodium Strontium Sulfur Tantalum Technetium Tellurium Terbium Thallium Thorium Thulium Tin Titanium Tungsten Ununoctium Ununpentium Ununseptium Ununtrium Uranium Vanadium Xenon Ytterbium Yttrium Zinc Zirconium'.split()


def make_table(verbose=False):
    "Return sample table and column names of all elements with some attributes."

    table = []
    for name in element_names:
        mw_path = name.lower() + '.mw'
        if not os.path.exists(mw_path):
            url = "https://en.wikipedia.org/w/index.php"
            url += "?title=Template:Infobox_%s&action=edit" % name.lower()
            ib = get_infobox_text(url)
            if verbose:
                print 'downloading %s...' % mw_path
            open(mw_path, 'w').write(ib.encode('utf-8'))
        else:
            if verbose:
                print 'loading %s...' % mw_path
            ib = open(mw_path).read().decode('utf-8')
        el = infobox2dict(ib)
        table.append((
            (el['name']).capitalize(), 
             el['symbol'],
             el['number'], 
             el.get('atomic radius', '?'), 
             el.get('atomic mass', '?'), 
             el.get('density gpcm3nrt', '?')
        ))
    column_names = 'Name Symbol Number Radius Mass Density_(g/cm^3)'.split()
    return table, column_names


def get_table(verbose=False):
    "Return a sample 'tabulated' table..."
    table, headers = make_table(verbose=verbose)
    return tabulate.tabulate(table, headers=headers)


def get_df(verbose=False):
    "Return a sample table as a Pandas DataFrame..."

    table, columns = make_table(verbose=verbose)
    df = pd.DataFrame(table, columns=columns)
    return df

    
if __name__ == '__main__':
    desc = 'Playing with the elements...'
    p = argparse.ArgumentParser(description=desc)
    p.add_argument('--verbose', action='store_true',
        help='Use verbose mode.')
    args = p.parse_args()
    print get_table(verbose=args.verbose)
