"""
    Dans l'ordre croissant ou decroissant
 
    Usage:
 
    >>> from Utila import MinToMax
    >>> MinToMax(a,b)  #the same list two times

    >>> from Utila import MaxToMin
    >>> MaxToMin(a,b)  #the same list two times

"""
def MinToMax(a, res):
    #test
    #Algorithme pour calculer le plus petit chifre 
    for j in range(0,len(a)):
        mini = a[0]
        k = 0
        for i in range(1,len(a)):
            if mini > a[i]:
                mini = a[i]  
                k = i          
        #je le met dans le tableau res        
        res[j] = mini
        #je detruie le plus petit
        a[k] = 100000 
    return(res)
def MaxToMin(a, res):
    #Algorithme pour calculer le plus grand chifre 
    for j in range(0,len(a)):
        mini = a[0]
        k = 0
        for i in range(1,len(a)):
            if mini < a[i]:
                mini = a[i]  
                k = i          
        #je le met dans le tableau res        
        res[j] = mini
        #je detruie le plus grand
        a[k] = 0 
    return(res)

            

