"""
Throttle	P_Oil	P_Air	P_Rail	TAirLM35	TH2OLM35
Lambdacyl1UF	Lambdacyl2UF	Lambdacyl3UF	Lambdacyl4UF
dtcalcus	RUN	ECUCPU	ECUMemory	ECUDisk	ECUChassisC	TH2OC	TAIRC	TFUELC	TOILC
CutOff	FilmCompensation	TorqueReduction	UserCorrection	Idle	LambdaCtrl
SAmapcyl1	SAmapcyl2	SAmapcyl3	SAmapcyl4
SAactcyl1	SAactcyl2	SAactcyl3	SAactcyl4
dtSATCScyl1	dtSATCScyl2	dtSATCScyl3	dtSATCScyl4
dtSAidlecyl1	dtSAidlecyl2	dtSAidlecyl3	dtSAidlecyl4
SAstartcyl1	SAstartcyl2	SAstartcyl3	SAstartcyl4
MjopenLoopCyl1	MjopenLoopCyl2	MjopenLoopCyl3	MjopenLoopCyl4
Mjfilmcyl1	Mjfilmcyl2	Mjfilmcyl3	Mjfilmcyl4
Mjactcyl1	Mjactcyl2	Mjactcyl3	Mjactcyl4
Tjactcyl1	Tjactcyl2	Tjactcyl3	Tjactcyl4
Mjstartcyl1	Mjstartcyl2	Mjstartcyl3	Mjstartcyl4
dtSAcyl14CA	dtSAcyl23CA
corrMjcyl1kMj	corrMjcyl2kMj	corrMjcyl3kMj	corrMjcyl4kMj
RPM	AngEvapWarning	Cycles	SMOTnoise	SYNClost	LambdaTargetact
AngEvapCA	SCAMnoise	dtSMOT
LambdaCtrlcorrcyl1	LambdaCtrlcorrcyl2	LambdaCtrlcorrcyl3	LambdaCtrlcorrcyl4
TCK1C	TCK2C	PacketNumber
Lambdacyl1	Lambdacyl2	Lambdacyl3	Lambdacyl4
TorqueReductionact	actMap
TScamb1	TScamb2	TCool1	TCool2	TCool3
FuelPump	H2OPump	Fan	Brake	Spare2
GearUP	GearDOWN
StartEN	VCUCPU	VCUMemory	VCUDisk
ChassisC	LapNumber	LapTime
SpeedFLKmh	SpeedFRKmh	SpeedRLKmh	SpeedRRKmh
Gear	Upshifts	Downshifts	TCSAct	LCSAct
AccTimems	AccFinSpeedKmh	SlipSX	SlipDX	Warning	GPSWITCH	SteeringAngle
FRHeightmm	FLHeightmm
PPneumBar	PbrakeFrontBar	PbrakeRearBar	ClutchPosPneum
BatteryCurrentA	BatteryVoltageV
RRHeightmm	RLHeightmm
AccXg	AccYg	AccZg
GyroXrad	GyroYrad	GyroZrad
ClutchPaddle
DamperFLmm	DamperFRmm	DamperRLmm	DamperRRmm
"""


class Names:
    """
    Another Luke pearl
    """

    # (Right, Wrong[, wrong ...])
    COMPATIBILITY_DICTIONARY = [
        ('DamperFL_mm', 'DamperFL', 'DamperFLmm'),
        ('DamperFR_mm', 'DamperFR', 'DamperFRmm'),
        ('DamperRL_mm', 'DamperRL', 'DamperFRmm'),
        ('DamperRR_mm', 'DamperRR', 'DamperRRmm'),
    ]

    Driver = {
        "SteeringAngle": 'SteeringAngle',
        "Throttle": 'Throttle',
        "Brakes": ('PbrakeFrontBar', 'PbrakeRearBar')
    }

    Engine = {
        "Cylinder": {
            "Lambda": ('Lambdacyl1', 'Lambdacyl2', 'Lambdacyl3', 'Lambdacyl4'),
            "InjectedMass": ('Mjactcyl1', 'Mjactcyl2', 'Mjactcyl3', 'Mjactcyl4'),
            "FilmMass": ('Mjfilmcyl1', 'Mjfilmcyl2', 'Mjfilmcyl3', 'Mjfilmcyl4')
        },
        "LambdaTarget": 'LambdaTargetact',
        "RPM": 'RPM'
    }

    Internal = {

    }

    Vehicle = {
        "PhonicWheels": ('SpeedFLKmh', 'SpeedFRKmh', 'SpeedRLKmh', 'SpeedRRKmh'),
        "Dampers": ('DamperFL_mm', 'DamperFR_mm', 'DamperRL_mm', 'DamperRR_mm'),
        "RideHeight": ('FLHeightmm', 'FRHeightmm', 'RLHeightmm', 'RRHeightmm')
    }

    IMU = {
        "Accelerometer": ('AccXg', 'AccYg', 'AccZg'),
        "Gyroscope": ('GyroXrad', 'GyroYrad', 'GyroZrad')
    }

    def __init__(self):
        return

    def fix(self, dataset):
        for lookup in self.COMPATIBILITY_DICTIONARY:
            right, errors = lookup[0], lookup[1:]
            for wrong in errors:
                if wrong in dataset.get_original_data().columns:
                    dataset.original_data[right] = dataset.original_data[wrong]
                    dataset.original_data[wrong] = None
