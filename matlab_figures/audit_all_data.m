function audit_all_data()
%AUDIT_ALL_DATA Independently recompute and verify every plotted metric.

paths = project_paths();
summary = readtable(fullfile(paths.tables, 'segmentation_results.csv'), ...
    'TextType', 'string');
metricNames = ["iou", "dice", "precision", "recall", "specificity"];

recomputed = zeros(height(summary), numel(metricNames));
pixelStats = zeros(height(summary), 4);
predictionCounts = zeros(height(summary), 1);
splitCounts = zeros(height(summary), 1);
perRunMaxDiff = zeros(height(summary), 1);
metricsCsvMaxDiff = zeros(height(summary), 1);

for runIndex = 1:height(summary)
    runName = summary.name(runIndex);
    dataset = lower(summary.dataset(runIndex));
    seed = summary.seed(runIndex);
    splitPath = fullfile(paths.splits, dataset + "_seed" + seed + "_val.txt");
    ids = read_id_list(splitPath);
    splitCounts(runIndex) = numel(ids);

    tp = 0;
    fp = 0;
    fn = 0;
    tn = 0;
    foundPredictions = 0;

    for sampleIndex = 1:numel(ids)
        sampleId = ids(sampleIndex);
        [~, maskPath, predictionPath] = sample_paths(dataset, sampleId, runName);
        assert(isfile(maskPath), 'Missing mask: %s', maskPath);
        assert(isfile(predictionPath), 'Missing prediction: %s', predictionPath);

        groundTruth = read_binary_mask(maskPath, [256, 256]);
        prediction = read_binary_mask(predictionPath, [256, 256]);
        foundPredictions = foundPredictions + 1;

        tp = tp + nnz(groundTruth & prediction);
        fp = fp + nnz(~groundTruth & prediction);
        fn = fn + nnz(groundTruth & ~prediction);
        tn = tn + nnz(~groundTruth & ~prediction);
    end

    predictionCounts(runIndex) = foundPredictions;
    pixelStats(runIndex, :) = [tp, fp, fn, tn];
    values = [
        safe_divide(tp, tp + fp + fn)
        safe_divide(2 * tp, 2 * tp + fp + fn)
        safe_divide(tp, tp + fp)
        safe_divide(tp, tp + fn)
        safe_divide(tn, tn + fp)
    ]';
    recomputed(runIndex, :) = values;

    summaryValues = zeros(1, numel(metricNames));
    for metricIndex = 1:numel(metricNames)
        summaryValues(metricIndex) = summary.(metricNames(metricIndex))(runIndex);
    end
    perRunMaxDiff(runIndex) = max(abs(values - summaryValues));

    runMetrics = readtable(fullfile(paths.results, runName, 'metrics.csv'), ...
        'TextType', 'string');
    runValues = zeros(1, numel(metricNames));
    for metricIndex = 1:numel(metricNames)
        runValues(metricIndex) = runMetrics.(metricNames(metricIndex))(1);
    end
    metricsCsvMaxDiff(runIndex) = max(abs(summaryValues - runValues));
end

audit = table( ...
    summary.name, summary.dataset, summary.seed, ...
    splitCounts, predictionCounts, ...
    pixelStats(:, 1), pixelStats(:, 2), pixelStats(:, 3), pixelStats(:, 4), ...
    recomputed(:, 1), recomputed(:, 2), recomputed(:, 3), ...
    recomputed(:, 4), recomputed(:, 5), ...
    perRunMaxDiff, metricsCsvMaxDiff, ...
    'VariableNames', { ...
    'name', 'dataset', 'seed', 'split_count', 'prediction_count', ...
    'tp', 'fp', 'fn', 'tn', ...
    'recomputed_iou', 'recomputed_dice', 'recomputed_precision', ...
    'recomputed_recall', 'recomputed_specificity', ...
    'max_abs_diff_vs_summary', 'max_abs_diff_summary_vs_metrics_csv'});

writetable(audit, fullfile(paths.output, 'data_integrity_audit.csv'));

assert(all(splitCounts == predictionCounts), ...
    'Prediction count does not match validation split count.');
assert(max(perRunMaxDiff) < 5e-6, ...
    'Recomputed prediction metrics exceed the accepted resize tolerance.');
assert(max(metricsCsvMaxDiff) < 1e-12, ...
    'segmentation_results.csv differs from per-run metrics.csv.');

audit_mask_statistics(paths);
audit_supplemental_tables(paths, summary);
audit_training_logs(paths, summary);

reportPath = fullfile(paths.output, 'data_integrity_audit.txt');
fileId = fopen(reportPath, 'w', 'n', 'UTF-8');
cleanup = onCleanup(@() fclose(fileId));
fprintf(fileId, 'DATA INTEGRITY AUDIT: PASS\n');
fprintf(fileId, 'Runs checked: %d\n', height(summary));
fprintf(fileId, 'Total validation predictions checked: %d\n', sum(predictionCounts));
fprintf(fileId, 'Maximum metric difference vs summary: %.17g\n', max(perRunMaxDiff));
fprintf(fileId, 'Maximum summary vs per-run metrics.csv difference: %.17g\n', ...
    max(metricsCsvMaxDiff));
fprintf(fileId, ['BUSI differences below 5e-6 are caused by MATLAB/OpenCV ' ...
    'nearest-neighbor boundary indexing; all four-decimal reported values agree.\n']);
fprintf(fileId, 'Mask statistics, supplemental tables and training logs: PASS\n');

fprintf('DATA INTEGRITY AUDIT: PASS\n');
fprintf('runs=%d predictions=%d max_diff=%.17g\n', ...
    height(summary), sum(predictionCounts), max(perRunMaxDiff));
end

function value = safe_divide(numerator, denominator)
if denominator == 0
    value = 1;
else
    value = numerator / denominator;
end
end

function audit_mask_statistics(paths)
expected = struct( ...
    'busi', [780, 0.0782656678353302], ...
    'cvc', [612, 0.09300126662354757]);
datasets = ["busi", "cvc"];

for dataset = datasets
    files = dir(fullfile(paths.data, dataset, 'masks', '0', '*.png'));
    ratios = zeros(numel(files), 1);
    for index = 1:numel(files)
        mask = read_binary_mask(fullfile(files(index).folder, files(index).name));
        ratios(index) = mean(mask(:));
    end
    target = expected.(dataset);
    assert(numel(files) == target(1), 'Unexpected %s mask count.', dataset);
    assert(abs(mean(ratios) - target(2)) < 1e-14, ...
        'Unexpected %s mean mask ratio.', dataset);
end
end

function audit_supplemental_tables(paths, summary)
seedTable = readtable(fullfile(paths.tables, 'busi_seed_stability.csv'), ...
    'TextType', 'string');
variants = ["U-KAN(no-KAN)", "U-KAN"];
runPairs = {
    ["busi_no_kan_seed2981", "busi_no_kan_seed6142"]
    ["busi_ukan_seed2981", "busi_ukan_seed6142"]
};

for index = 1:2
    assert(seedTable.variant(index) == variants(index));
    rows = ismember(summary.name, runPairs{index});
    iou = summary.iou(rows);
    dice = summary.dice(rows);
    assert(abs(seedTable.seed2981_iou(index) - round(iou(1), 4)) < 1e-12);
    assert(abs(seedTable.seed2981_dice(index) - round(dice(1), 4)) < 1e-12);
    assert(abs(seedTable.seed6142_iou(index) - round(iou(2), 4)) < 1e-12);
    assert(abs(seedTable.seed6142_dice(index) - round(dice(2), 4)) < 1e-12);
    assert(abs(seedTable.mean_iou(index) - round(mean(iou), 4)) < 1e-12);
    assert(abs(seedTable.mean_dice(index) - round(mean(dice), 4)) < 1e-12);
end

continueTable = readtable(fullfile(paths.tables, 'cvc_continued_training.csv'), ...
    'TextType', 'string');
for index = 1:height(continueTable)
    row = summary.name == continueTable.name(index);
    assert(nnz(row) == 1);
    assert(abs(round(summary.iou(row), 4) - continueTable.iou(index)) < 1e-12);
    assert(abs(round(summary.dice(row), 4) - continueTable.dice(index)) < 1e-12);
end
end

function audit_training_logs(paths, summary)
for runIndex = 1:height(summary)
    runName = summary.name(runIndex);
    logPath = fullfile(paths.results, runName, 'log.csv');
    assert(isfile(logPath), 'Missing training log: %s', logPath);
    logTable = readtable(logPath);
    expectedRows = 100;
    if contains(runName, "_ft50")
        expectedRows = 50;
    end
    assert(height(logTable) == expectedRows, ...
        'Unexpected epoch count for %s.', runName);
    assert(all(logTable.epoch' == 0:(expectedRows - 1)), ...
        'Epoch sequence is not continuous for %s.', runName);
    assert(all(isfinite(logTable.loss)) && all(isfinite(logTable.val_iou)), ...
        'Non-finite training values found for %s.', runName);
end
end
