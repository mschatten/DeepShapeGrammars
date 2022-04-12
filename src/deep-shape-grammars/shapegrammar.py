#!/usr/bin/env python3

import templatematching as tm

def new_grammar():
    print( "Creating new grammar ..." )

def apply_rule( rule, image ):
    m = tm.match( image, rule.LHS )
    
