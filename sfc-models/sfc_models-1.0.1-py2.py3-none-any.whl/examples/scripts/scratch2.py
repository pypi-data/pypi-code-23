from sfc_models.objects import *
from sfc_models.examples.Quick2DPlot import Quick2DPlot
register_standard_logs('output', 'example')
# Create model, country
mod = Model()
can = Country(mod, 'CA', 'Canada')
# Create sectors
gov = ConsolidatedGovernment(can, 'GOV', 'Government')
hh = Household(can, 'HH', 'Household')
bus = FixedMarginBusiness(can, 'BUS', 'Business Sector')
# Create the linkages between sectors
tax = TaxFlow(can, 'TF', 'TaxFlow', .2)
labour = Market(can, 'LAB', 'Labour market')
goods = Market(can, 'GOOD', 'Goods market')
# set the exogenous variable
mod.AddExogenous('GOV', 'DEM_GOOD', '[0.,]*5 + [20.,] * 105')
# Build the model
mod.main()
k = mod.GetTimeSeries('k', cutoff=30)
goods_produced = mod.GetTimeSeries('BUS__SUP_GOOD', cutoff=30)
Quick2DPlot(k, goods_produced, 'Goods Produced (National Output)')
