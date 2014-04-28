import ply.yacc as yacc
from .lexer import tokens

def p_node(p):
    """
    node : cuisine_type
        | subzone_type
        | dead_state
    """
    p[0] = ('node', p[1])

def p_dead_state(p):
    """
    dead_state :
    """
    pass

def p_rel(p):
    """
    rel : to_cuisine_rel
        | to_subzone_rel
    """
    p[0] = ('rel', p[1])

def p_cuisine_type(p):
    """
    cuisine_type : CUISINE
            | CUISINE AND cuisine_type
            | CUISINE rel
    """
    p[0] = ('cuisine_type',) + tuple(p[1:])

def p_subzone_type(p):
    """
    subzone_type : SUBZONE
            | SUBZONE AND subzone_type
            | SUBZONE rel
    """
    p[0] = ('subzone_type',) + tuple(p[1:])

def p_to_cuisine_rel(p):
    """
    to_cuisine_rel : SERVING cuisine_type
            | SERVES cuisine_type
            | WITH cuisine_type
    """
    p[0] = ('to_cuisine_rel', p[1], p[2])

def p_to_subzone_rel(p):
    """
    to_subzone_rel : NEAR subzone_type
            | IN subzone_type
    """
    p[0] = ('to_subzone_rel', p[1], p[2])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error at '%s'" % repr(p)) #p.value)


def build_tree(searchInput):
    parser = yacc.yacc(start='node')
    return parser.parse(searchInput)