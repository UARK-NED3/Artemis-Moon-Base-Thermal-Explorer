function result = runLunarThermalScenario(scenarioPath)
%RUNLUNARTHERMALSCENARIO Run the shared constant-forcing JSON schema with RK4.

scenario = jsondecode(fileread(scenarioPath));
node = scenario.thermal_node;
fluxes = scenario.external_fluxes;
temperatureK = scenario.initial_temperature_k;
durationS = scenario.duration_s;
timeStepS = scenario.time_step_s;
steps = ceil(durationS / timeStepS);
integratedNetEnergyJ = 0.0;

for stepIndex = 1:steps
    dtS = min(timeStepS, durationS - (stepIndex - 1) * timeStepS);
    derivative = @(T) lunarThermalHeatRates(node, fluxes, T).net_power_w / node.heat_capacity_j_per_k;
    k1 = derivative(temperatureK);
    k2 = derivative(temperatureK + 0.5 * dtS * k1);
    k3 = derivative(temperatureK + 0.5 * dtS * k2);
    k4 = derivative(temperatureK + dtS * k3);
    averageDerivative = (k1 + 2*k2 + 2*k3 + k4) / 6;
    temperatureK = temperatureK + dtS * averageDerivative;
    integratedNetEnergyJ = integratedNetEnergyJ + node.heat_capacity_j_per_k * dtS * averageDerivative;
end

result.scenario_id = scenario.scenario_id;
result.initial_temperature_k = scenario.initial_temperature_k;
result.final_temperature_k = temperatureK;
result.duration_s = durationS;
result.time_step_s = timeStepS;
result.integrated_net_energy_j = integratedNetEnergyJ;
result.energy_residual_j = node.heat_capacity_j_per_k * (temperatureK - scenario.initial_temperature_k) - integratedNetEnergyJ;
result.final_heat_rates = lunarThermalHeatRates(node, fluxes, temperatureK);
end
