# How to build a complex model

import jscatter as js

#build a complex model of different components

def particlesWithInteraction(q,Ra,Rb,molarity,bgr,contrast,collimation=None,beta=True):
    """
    Particles with interaction and ellipsoid form factor as a model for e.g. dense protein solutions.

    Document your model if needed for later use that you know what you did and why.
    Or make it short without all the nasty documentation for testing.
    The example neglects the protein exact shape and non constant scattering length density.
    Proteins are more potato shaped  and nearly never like a ellipsoid or sphere.
    So this model is only valid at low Q as an approximation.

    Parameters
    ----------
    q : float
        Wavevector
    Ra,Rb : float
        Radius
    molarity : float
        Concentration in mol/l
    contrast : float
        Contrast between ellipsoid and solvent.
    bgr : float
        Background e.g. incoherent scattering
    collimation : float
        Collimation length for SANS. For SAXS use None.
    beta : bool
        True include asymmetry factor beta of
        M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    Returns
    -------
        dataArray

    Notes
    -----
    Explicitly:
    **The return value can be a dataArray OR only Y values**. Both is working for fitting.

    """
    # We need to multiply form factor and structure factor and add an additional background.
    # formfactor of ellipsoid returns dataArray with beta at last column.
    ff=js.ff.ellipsoid(q, Ra, Rb,SLD=contrast,beta=beta)
    V=ff.EllipsoidVolume
    # the structure factor returns also dataArray
    # we need to supply a radius calculated from Ra Rb, this is an assumption of effective radius for the interaction.
    R=(Ra*Rb*Rb)**(1/3.)
    # the volume fraction is concentration * volume
    # the units have to be converted as V is usually nm**3 and concentration is mol/l
    sf=js.sf.PercusYevick(q,R,molarity=molarity)
    if beta:
        # beta is asymmetry factor according to M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).
        # correction to apply for the structure factor
        # noinspection PyProtectedMember
        sf.Y=1+ff._beta*(sf.Y-1)
    #
    # molarity (mol/l) with conversion to number/nm**3 result is in cm**-1
    ff.Y=molarity*6.023e23/(1000*1e7**2)*ff.Y*sf.Y+bgr
    # add parameters for later use; ellipsoid parameters are already included in ff
    # if data are saved these are included in the file as documentation
    # or can be used for further calculations e.g. if volume fraction is needed (V*molarity)
    ff.R=R
    ff.bgr=bgr
    ff.Volume=V
    ff.molarity=molarity
    # for small angle neutron scattering we may need instrument resolution smearing
    if collimation is not None:
        # For SAX we set collimation=None and this is ignored
        # For SANS we set some reasonable values as 2000 (mm) or 20000 (mm)
        # as attribute in the data we want to fit.
        result=js.sas.resFunct(ff, collimation, 10, collimation, 10, 0.7, 0.15)
    else:
        result=ff
    #we return the complex model for fitting
    return result

p=js.grace()
q=js.loglist(0.1,5,300)
for m in [0.01,0.1,1,2,3,4]:
    data=particlesWithInteraction(q,Ra=3,Rb=4,molarity=m*1e-3,bgr=0,contrast=1)
    p.plot(data,le='c= $molarity M')

p.legend()
p.yaxis(min=100,scale='l',label='I(Q) / cm\S-1',tick=[10,9])
p.xaxis(scale='n',label='Q / nm\S-1')
p.title('Ellipsoidal particles with interaction')
p.subtitle('Ra=3, Rb=4 and PercusYevick structure factor')
# Hint for fitting SANS data or other parameter dependent fit:
# For a combined fit of several collimation distances each dataset should contain an attribute data.collimation.
# This is automatically used in the fit, if there is not explicit fit parameter with this name.

if 0:
    p.save('interactingParticles.agr')
    p.save('interactingParticles.jpeg')
