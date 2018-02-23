def cijfer(waarde, grens_onder=None, drempel_onder=None, drempel_boven=None, grens_boven=None):
    cijfer = 0
    
    R = waarde
    M = grens_onder
    L = drempel_onder
    D = drempel_boven
    G = grens_boven
    
    # alleen bovengrenzen
    if drempel_boven and not drempel_onder:
        if R<=D and D is not G:
            cijfer = 10-2*R/D
        elif R<=D:
            cijfer = 10-4*R/D
        elif R<=G and D is not G:
            cijfer = 8-2*(R-D)/(G-D)
        elif D is not G:
            cijfer = 6-2*(R-G)/(G-D)
        else:
            cijfer = 6-4*(R-G)/D
    
    # alleen ondergrenzen
    elif drempel_onder and not drempel_boven:
        if R>=L and L is not M:
            cijfer = 8+2*(R-L)/(L-M)
        elif R>=L:
            cijfer = 6+6*(R-L)/L
        elif R>=M and L is not M:
            cijfer = 6+2*(R-M)/(L-M)
        else:
            cijfer = 6-6*(M-R)/M

    # onder en bovengrenzen
    else:
        A = D-(D-L)/2
        if R>G and G is not D:
            cijfer = 6-2*(R-G)/(G-D)
        elif R>=G:
            cijfer = 6-4*(R-G)/(G-A)
        elif R<=G and R>D:
            cijfer = 8-2*(R-D)/(G-D)
        elif R<=D and R>=A and G is not D:
            cijfer = 10-2*(R-A)/(D-A)
        elif R<=D and R>=A:
            cijfer = 10-4*(R-A)/(D-A)
        elif R<A and R>=L and L is not M:
            cijfer = 8+2*(R-L)/(A-L)
        elif R<A and R>=L:
            cijfer = 6+4*(R-L)/(A-L)
        elif R<L and R>=M and L is not M:
            cijfer = 6+2*(R-M)/(L-M)
        else:
            cijfer = 6-6*(M-R)/M
    
    if cijfer > 10:
        return 10
    elif cijfer < 0:
        return 0
    else:
        return float(cijfer)
