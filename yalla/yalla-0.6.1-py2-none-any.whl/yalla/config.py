#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4
#
"""
module pour gerer les parametres du calcul
"""

import os

from messages import signal, CRITICAL

class Config:
    """
        Classe pour gerer les parametres du calcul

        Les parametres sont dans un fichier config_TSAR3D
        Les parametres sont stockes dans un dictionnaire
        d_val_param
        On va chercher la valeur du parametre param en cherchant
        le mot cle param dans le fichier
    """

    def __init__(self, file_config_name):

        self.fic_config = file_config_name

        if (os.path.isfile(self.fic_config) == False):
            signal(CRITICAL, "Fichier %s inexistant"%file_config_name)

        self.d_params = {}
        fic = open(self.fic_config, "r")
        for ligne in fic.readlines():
            chaine = str.split(ligne)
            if len(chaine):
                self.d_params[chaine[0]] = chaine[1:]

        fic.close()

    def check_mandatory_params(self, l_param_obligatoire):
        """
        Quelques tests simples sur la coherence des donnï¿½es
        """
        for param in l_param_obligatoire:
            if param not in self.d_params.keys():
                signal(CRITICAL,
                       param
                       +" ne figure pas dans le fichier de configuration "
                       +self.fic_config)
            if (len(self.d_params[param]) == 0):
                signal(CRITICAL,
                       "pour "+param
                       +" valeur non renseignee "
                       +" dans le fichier de configuration "
                       +self.fic_config)

    def get_param(self, name, index=None):
        """
        renvoie la premiere valeur possible prise par un parametre
        """
        if name not in self.d_params.keys():
            signal(CRITICAL,
                   "parameter '%s'  not defined in configuration"%(name))
        if index == None and len(self.d_params[name])>1:
            signal(CRITICAL,
                   "asking for 1 parameter '%s' with no index and more \
                   than one value is defined in configuration! \
                   please choose one of them : \n\t%s"%
                (name, "\n\t".join(tuple(self.d_params[name]))))
        if index == None:
            index = 0
        if index >= len(self.d_params[name]):
            signal(CRITICAL,
                   "asking for %s th field for parameter '%s'  \
                   that only counts %s in configuration\n\t%s"%
                (index, name, len(self.d_params[name]), self.fic_config))
        return self.d_params[name][index]

    def get_params(self, name):
        """
        renvoie toutes les valeurs possible d'un parametre
        """
        if name in self.d_params.keys():
            return self.d_params[name]
        else:
            signal(CRITICAL,
                   "parameter '%s'  not defined in configuration"%(name)) 

    def set_params(self, name, values):
        """
        initialise les valeur d'un parametre
        """
        self.d_params[name]=list(values)
        
    def set_param(self, name, index, value):
        """
        initialisela valeur d'un parametre
        """
        if name in self.d_params.keys():
            if len(self.d_params.keys())>index:
                self.d_params[name][index] = value
            else:
                signal(CRITICAL,
                       "parameter '%s[%d]'  not defined in configuration" %\
                       (name, index))
        else:
            signal(CRITICAL,
                   "parameter '%s[%d]'  not defined in configuration" %\
                   (name, index)) 

    def nb_param(self, name):
        """
        renvoie le nombre de valeurs pouvant etre pris par un parametre
        """
        if name in self.d_params.keys():
            return len(self.d_params[name])
        else:
            signal(CRITICAL,
                   "parameter '%s'  not defined in configuration"%(name))

    def check_same_nb(self, *args):   
        """
        verifie si ?????
        """
        if len(args)==0:
            signal(CRITICAL, "checkSameNb called with an empty list!")
        if len(args)>1:
            num = self.nb_param(args[0])
            for par in args[1:]:
                if not(self.nb_param(par)==num):
                    signal(CRITICAL, "Different number for parameters : %s"%
                         (",".join(
                                map(lambda x:" %s for '%s'" % \
                                    (self.nb_param(x), x), args))))


    def check_file_exist(self, file_parameters):
        """
        verifie si les noms de fichiers passé en argument
        correspondent bien a des fichiers existants
        """
        for param in file_parameters:
            file_names = self.get_params(param)
	    for file_name in file_names:
                if (os.path.isfile(file_name) == False):
                    signal(CRITICAL,
                       "file '%s' corresponding to param '%s' does not exist"
                       % (file_name, param))

    def check_dir_exist(self, dir_parameters):
        """
        verifie si les noms de repertoires passé en argument
        correspondent bien a des repertoires existants
        """
        for param in dir_parameters:
            dir_names = self.get_params(param)
            for dir_name in dir_names:
                if (os.path.isdir(dir_name) == False):
                    signal(CRITICAL,
                       "dir '%s' corresponding to param '%s' does not exist"\
                       % (dir_name, param))





