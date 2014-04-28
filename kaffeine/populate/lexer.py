import ply.lex as lex

tokens = [
    'CUISINE',
	'SUBZONE',
	'NEAR',
	'AND',
	'IN',
	'SERVING',
	'SERVES',
	'WITH'
]


def t_CUISINE(t):
    r'(cuisine\d{1})'
    return t

def t_SUBZONE(t):
    r'(subzone\d{1})'
    return t

def t_IN(t):
    r'(in)'
    return t

def t_NEAR(t):
    r'(near)'
    return t

def t_AND(t):
    r'(and)'
    return t

def t_SERVING(t):
    r'(serving)'
    return t

def t_SERVES(t):
    r'(serves)'
    return t

def t_WITH(t):
    r'(with)'
    return t


def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()