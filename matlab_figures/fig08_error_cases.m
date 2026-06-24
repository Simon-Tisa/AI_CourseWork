function fig08_error_cases()
%FIG08_ERROR_CASES Select under- and over-segmentation examples by error ratio.

paths = project_paths();
datasets = ["busi", "cvc"];
datasetLabels = ["BUSI", "CVC-ClinicDB"];
splitFiles = ["busi_seed2981_val.txt", "cvc_seed2981_val.txt"];
runNames = ["busi_ukan_seed2981", "cvc_ukan_seed2981"];

selectedDataset = strings(4, 1);
selectedId = strings(4, 1);
selectedDice = zeros(4, 1);
selectedType = strings(4, 1);
selectedFpRatio = zeros(4, 1);
selectedFnRatio = zeros(4, 1);
writeIndex = 1;

for datasetIndex = 1:2
    ids = read_id_list(fullfile(paths.splits, splitFiles(datasetIndex)));
    diceValues = nan(numel(ids), 1);
    fpRatios = nan(numel(ids), 1);
    fnRatios = nan(numel(ids), 1);
    for sampleIndex = 1:numel(ids)
        [~, maskPath, predictionPath] = sample_paths( ...
            datasets(datasetIndex), ids(sampleIndex), runNames(datasetIndex));
        groundTruth = read_binary_mask(maskPath, [256, 256]);
        prediction = read_binary_mask(predictionPath, [256, 256]);
        denominator = nnz(groundTruth) + nnz(prediction);
        if denominator == 0
            diceValues(sampleIndex) = 1;
        else
            diceValues(sampleIndex) = 2 * nnz(groundTruth & prediction) / denominator;
        end
        targetArea = max(nnz(groundTruth), 1);
        fpRatios(sampleIndex) = nnz(~groundTruth & prediction) / targetArea;
        fnRatios(sampleIndex) = nnz(groundTruth & ~prediction) / targetArea;
    end

    valid = diceValues > 0.05 & diceValues < 0.92;
    candidateIndices = find(valid);
    [~, fpOrder] = sort(fpRatios(candidateIndices), 'descend');
    [~, fnOrder] = sort(fnRatios(candidateIndices), 'descend');
    chosen = [candidateIndices(fpOrder(1)), candidateIndices(fnOrder(1))];
    failureTypes = ["过分割主导", "漏分割主导"];
    for localIndex = 1:numel(chosen)
        selectedDataset(writeIndex) = datasets(datasetIndex);
        selectedId(writeIndex) = ids(chosen(localIndex));
        selectedDice(writeIndex) = diceValues(chosen(localIndex));
        selectedType(writeIndex) = failureTypes(localIndex);
        selectedFpRatio(writeIndex) = fpRatios(chosen(localIndex));
        selectedFnRatio(writeIndex) = fnRatios(chosen(localIndex));
        writeIndex = writeIndex + 1;
    end
end

fig = new_paper_figure(1700, 1450);
layout = tiledlayout(fig, 4, 4, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, 'U-KAN 典型困难样本与误差区域', ...
    'FontSize', 18, 'FontWeight', 'bold');
columnTitles = ["原图", "专家标注", "U-KAN 预测", "误差叠加"];

for rowIndex = 1:4
    dataset = selectedDataset(rowIndex);
    sampleId = selectedId(rowIndex);
    runName = dataset + "_ukan_seed2981";
    [imagePath, maskPath, predictionPath] = sample_paths(dataset, sampleId, runName);

    image = ensure_rgb(imread(imagePath));
    image = imresize(image, [256, 256], 'bilinear');
    groundTruth = read_binary_mask(maskPath, [256, 256]);
    prediction = read_binary_mask(predictionPath, [256, 256]);
    overlay = overlay_prediction_errors(image, groundTruth, prediction);

    panels = {image, groundTruth, prediction, overlay};
    for columnIndex = 1:4
        nexttile;
        imshow(panels{columnIndex});
        if rowIndex == 1
            title(columnTitles(columnIndex), 'FontSize', 10);
        end
        if columnIndex == 1
            if dataset == "busi"
                datasetLabel = datasetLabels(1);
            else
                datasetLabel = datasetLabels(2);
            end
            ylabel(sprintf('%s / %s\n%s, Dice=%.3f', ...
                datasetLabel, sampleId, selectedType(rowIndex), selectedDice(rowIndex)), ...
                'Interpreter', 'none', 'FontWeight', 'bold');
        end
    end
end

audit = table( ...
    selectedDataset, selectedId, selectedType, selectedDice, ...
    selectedFpRatio, selectedFnRatio, ...
    'VariableNames', { ...
    'dataset', 'sample_id', 'failure_type', 'dice', 'fp_ratio', 'fn_ratio'});
writetable(audit, fullfile(paths.output, 'fig08_error_cases_selected.csv'));

annotation(fig, 'textbox', [0.15, 0.005, 0.7, 0.03], ...
    'String', '误差叠加：绿色=正确前景，红色=过分割，蓝色=漏分割', ...
    'EdgeColor', 'none', 'HorizontalAlignment', 'center', 'FontSize', 10);

export_paper_figure(fig, "fig08_error_cases_matlab");
end
