function exploreLunarThermal()
%EXPLORELUNARTHERMAL Prediction-test-explain interaction for synthetic lunar-night cases.

root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
baselinePath = fullfile(root, 'config', 'scenarios', 'lunar_night_survival.json');
options = {'Higher internal load', 'Larger radiator'};
optionPaths = { ...
    fullfile(root, 'config', 'scenarios', 'lunar_night_high_load.json'), ...
    fullfile(root, 'config', 'scenarios', 'lunar_night_large_radiator.json')};

choice = menu('Synthetic lunar-night lesson: choose a change', options{:});
if choice == 0
    return
end
prediction = input('Will final temperature Rise, Fall, or Stay the same? ', 's');
baseline = runLunarThermalScenario(baselinePath);
candidate = runLunarThermalScenario(optionPaths{choice});
deltaK = candidate.final_temperature_k - baseline.final_temperature_k;
if deltaK > 0.01
    actual = 'Rise';
elseif deltaK < -0.01
    actual = 'Fall';
else
    actual = 'Stay the same';
end

fprintf('\nChange: %s\nBaseline final temperature: %.2f K\nChanged-case final temperature: %.2f K\nComputed change: %s\n', ...
    options{choice}, baseline.final_temperature_k, candidate.final_temperature_k, actual);
normalizedPrediction = lower(strtrim(prediction));
if (strcmp(normalizedPrediction, 'rise') && strcmp(actual, 'Rise')) || ...
        (strcmp(normalizedPrediction, 'fall') && strcmp(actual, 'Fall')) || ...
        ((strcmp(normalizedPrediction, 'stay') || strcmp(normalizedPrediction, 'stay the same')) && strcmp(actual, 'Stay the same'))
    fprintf('Prediction check: matches the model.\n');
else
    fprintf('Prediction check: does not match the model.\n');
end
fprintf('This is a synthetic screening-level lesson, not an Artemis operational or flight model.\n');
end
