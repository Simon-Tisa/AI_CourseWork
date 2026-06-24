function metrics = collect_per_image_metrics(dataset, runNames, modelLabels)
%COLLECT_PER_IMAGE_METRICS Compute per-image segmentation error statistics.

paths = project_paths();
dataset = lower(string(dataset));
if dataset == "busi"
    splitFile = 'busi_seed2981_val.txt';
else
    splitFile = 'cvc_seed2981_val.txt';
end
ids = read_id_list(fullfile(paths.splits, splitFile));

rowCount = numel(ids) * numel(runNames);
sampleIds = strings(rowCount, 1);
models = strings(rowCount, 1);
dice = zeros(rowCount, 1);
iou = zeros(rowCount, 1);
maskRatio = zeros(rowCount, 1);
fpRatio = zeros(rowCount, 1);
fnRatio = zeros(rowCount, 1);

row = 1;
for sampleIndex = 1:numel(ids)
    sampleId = ids(sampleIndex);
    [~, maskPath] = sample_paths(dataset, sampleId);
    groundTruth = read_binary_mask(maskPath, [256, 256]);
    targetArea = max(nnz(groundTruth), 1);

    for modelIndex = 1:numel(runNames)
        [~, ~, predictionPath] = sample_paths(dataset, sampleId, runNames(modelIndex));
        prediction = read_binary_mask(predictionPath, [256, 256]);
        tp = nnz(groundTruth & prediction);
        fp = nnz(~groundTruth & prediction);
        fn = nnz(groundTruth & ~prediction);

        sampleIds(row) = sampleId;
        models(row) = modelLabels(modelIndex);
        dice(row) = safe_divide(2 * tp, 2 * tp + fp + fn);
        iou(row) = safe_divide(tp, tp + fp + fn);
        maskRatio(row) = nnz(groundTruth) / numel(groundTruth);
        fpRatio(row) = fp / targetArea;
        fnRatio(row) = fn / targetArea;
        row = row + 1;
    end
end

metrics = table(sampleIds, models, dice, iou, maskRatio, fpRatio, fnRatio, ...
    'VariableNames', { ...
    'sample_id', 'model', 'dice', 'iou', 'mask_ratio', 'fp_ratio', 'fn_ratio'});
end

function value = safe_divide(numerator, denominator)
if denominator == 0
    value = 1;
else
    value = numerator / denominator;
end
end
