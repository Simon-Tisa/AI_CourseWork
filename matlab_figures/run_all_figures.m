function run_all_figures()
%RUN_ALL_FIGURES Generate every MATLAB-based data figure.

close all force;
clc;

jobs = {
    @fig01_dataset_samples
    @fig02_mask_ratio_distribution
    @fig03_main_results
    @fig04_busi_training_curves
    @fig05_cvc_training_curves
    @fig06_busi_prediction_comparison
    @fig07_cvc_prediction_comparison
    @fig08_error_cases
    @fig09_supplemental_experiments
    @fig10_efficiency_tradeoff
    @fig11_metric_heatmap
    @fig12_failure_distribution_size
    @fig13_error_composition
    @fig14_runtime_evidence
    @fig15_runtime_screenshots
};

fprintf('MATLAB data figure generation started.\n');
failures = strings(0, 1);
for index = 1:numel(jobs)
    name = func2str(jobs{index});
    fprintf('[%02d/%02d] %s\n', index, numel(jobs), name);
    try
        jobs{index}();
    catch exception
        failures(end + 1, 1) = name + ": " + string(exception.message); %#ok<AGROW>
        fprintf(2, 'FAILED %s: %s\n', name, exception.message);
    end
end
if ~isempty(failures)
    error('MATLABFigures:GenerationFailed', ...
        'One or more figures failed:\n%s', strjoin(failures, newline));
end
fprintf('MATLAB data figure generation completed.\n');
end
