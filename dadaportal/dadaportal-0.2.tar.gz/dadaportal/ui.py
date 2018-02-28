import horetu
import dadaportal

def ui():
    horetu.cli(horetu.Program({
        'build': dadaportal.build,
        'check': dadaportal.check,
        'skeleton': [
            dadaportal.skeleton.configure,
            dadaportal.skeleton.listing,
            dadaportal.skeleton.nfsn,
            dadaportal.skeleton.sdf,
            dadaportal.skeleton.permissions,
        ],
    }, name='dadaportal'))
