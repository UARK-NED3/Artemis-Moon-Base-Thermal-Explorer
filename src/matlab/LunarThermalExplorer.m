function fig = LunarThermalExplorer()
%LUNARTHERMALEXPLORER Interactive GUI for a synthetic lunar-night lesson.
% Values are illustrative and do not represent Artemis hardware or operations.

fig = uifigure('Name', 'Artemis Moon Base Thermal Explorer', 'Position', [100 100 1050 650]);
mainGrid = uigridlayout(fig, [2 2]);
mainGrid.RowHeight = {'1x', 145};
mainGrid.ColumnWidth = {'1x', 300};

ax = uiaxes(mainGrid);
ax.Layout.Row = 1;
ax.Layout.Column = 1;
title(ax, 'Synthetic lunar-night temperature response');
xlabel(ax, 'Time (h)');
ylabel(ax, 'Temperature (K)');
barAx = uiaxes(mainGrid);
barAx.Layout.Row = 2;
barAx.Layout.Column = 1;
title(barAx, 'Final-state heat-rate balance');
ylabel(barAx, 'Power (W), positive into node');

panel = uipanel(mainGrid, 'Title', 'Model inputs and results');
panel.Layout.Row = [1 2];
panel.Layout.Column = 2;
controls = uigridlayout(panel, [9 1]);
controls.RowHeight = {'fit', 'fit', 'fit', 'fit', 'fit', 'fit', 'fit', 'fit', '1x'};

uilabel(controls, 'Text', 'Internal dissipation (W)');
powerSlider = uislider(controls, 'Limits', [0 200], 'Value', 35, 'MajorTicks', [0 50 100 150 200]);
uilabel(controls, 'Text', 'Radiator area (m²)');
areaSlider = uislider(controls, 'Limits', [0.1 2.0], 'Value', 0.6, 'MajorTicks', [0.1 0.5 1.0 1.5 2.0]);
uilabel(controls, 'Text', 'Emissivity (-)');
emissivitySlider = uislider(controls, 'Limits', [0.1 1.0], 'Value', 0.82, 'MajorTicks', [0.1 0.4 0.7 1.0]);
resultLabel = uilabel(controls, 'Text', '', 'WordWrap', 'on', 'FontWeight', 'bold');
uilabel(controls, 'Text', 'Synthetic screening-level model. It excludes site-specific boundary conditions, dust, detailed geometry, conduction networks, and controls.', 'WordWrap', 'on');

powerSlider.ValueChangingFcn = @(~, event) update(event.Value, areaSlider.Value, emissivitySlider.Value);
areaSlider.ValueChangingFcn = @(~, event) update(powerSlider.Value, event.Value, emissivitySlider.Value);
emissivitySlider.ValueChangingFcn = @(~, event) update(powerSlider.Value, areaSlider.Value, event.Value);
powerSlider.ValueChangedFcn = @(~, event) update(event.Value, areaSlider.Value, emissivitySlider.Value);
areaSlider.ValueChangedFcn = @(~, event) update(powerSlider.Value, event.Value, emissivitySlider.Value);
emissivitySlider.ValueChangedFcn = @(~, event) update(powerSlider.Value, areaSlider.Value, event.Value);
update(powerSlider.Value, areaSlider.Value, emissivitySlider.Value);

    function update(internalPowerW, radiatorAreaM2, emissivity)
        node.heat_capacity_j_per_k = 40000.0;
        node.radiator_area_m2 = radiatorAreaM2;
        node.emissivity = emissivity;
        node.solar_absorptivity = 0.25;
        node.solar_area_m2 = 0.5;
        node.albedo_area_m2 = 0.5;
        node.lunar_ir_area_m2 = 0.5;
        node.space_view_factor = 0.8;
        fluxes.internal_power_w = internalPowerW;
        fluxes.direct_solar_irradiance_w_per_m2 = 0.0;
        fluxes.albedo_irradiance_w_per_m2 = 0.0;
        fluxes.lunar_ir_irradiance_w_per_m2 = 0.0;
        fluxes.radiative_sink_temperature_k = 3.0;
        durationS = 12 * 3600;
        timeStepS = 60;
        steps = ceil(durationS / timeStepS);
        timeS = zeros(steps + 1, 1);
        temperatureK = zeros(steps + 1, 1);
        temperatureK(1) = 270.0;
        for index = 1:steps
            dtS = min(timeStepS, durationS - timeS(index));
            deriv = @(T) lunarThermalHeatRates(node, fluxes, T).net_power_w / node.heat_capacity_j_per_k;
            k1 = deriv(temperatureK(index));
            k2 = deriv(temperatureK(index) + 0.5 * dtS * k1);
            k3 = deriv(temperatureK(index) + 0.5 * dtS * k2);
            k4 = deriv(temperatureK(index) + dtS * k3);
            temperatureK(index + 1) = temperatureK(index) + dtS * (k1 + 2*k2 + 2*k3 + k4) / 6;
            timeS(index + 1) = timeS(index) + dtS;
        end
        finalRates = lunarThermalHeatRates(node, fluxes, temperatureK(end));
        plot(ax, timeS / 3600, temperatureK, 'LineWidth', 2);
        grid(ax, 'on');
        bar(barAx, categorical({'Internal', 'Radiation', 'Net'}), [internalPowerW, -finalRates.radiated_power_w, finalRates.net_power_w]);
        grid(barAx, 'on');
        resultLabel.Text = sprintf('Final temperature: %.2f K (%.2f C)\nNet heat rate at final state: %.2f W', ...
            temperatureK(end), temperatureK(end) - 273.15, finalRates.net_power_w);
    end
end
