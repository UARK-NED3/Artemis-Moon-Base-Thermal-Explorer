function rates = lunarThermalHeatRates(node, fluxes, temperatureK)
%LUNARTHERMALHEATRATES Screening-level single-node lunar thermal balance.
% All inputs use SI units. Heat rates are positive into the thermal node.

sigma = 5.670374419e-8;
solarAbsorbedW = node.solar_absorptivity * node.solar_area_m2 * fluxes.direct_solar_irradiance_w_per_m2;
albedoAbsorbedW = node.solar_absorptivity * node.albedo_area_m2 * fluxes.albedo_irradiance_w_per_m2;
lunarIrAbsorbedW = node.emissivity * node.lunar_ir_area_m2 * fluxes.lunar_ir_irradiance_w_per_m2;
radiatedPowerW = node.emissivity * sigma * node.radiator_area_m2 * node.space_view_factor * ...
    (temperatureK^4 - fluxes.radiative_sink_temperature_k^4);
absorbedPowerW = fluxes.internal_power_w + solarAbsorbedW + albedoAbsorbedW + lunarIrAbsorbedW;

rates.internal_power_w = fluxes.internal_power_w;
rates.solar_absorbed_w = solarAbsorbedW;
rates.albedo_absorbed_w = albedoAbsorbedW;
rates.lunar_ir_absorbed_w = lunarIrAbsorbedW;
rates.radiated_power_w = radiatedPowerW;
rates.absorbed_power_w = absorbedPowerW;
rates.net_power_w = absorbedPowerW - radiatedPowerW;
end
