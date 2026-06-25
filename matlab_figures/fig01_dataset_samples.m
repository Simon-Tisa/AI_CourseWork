function fig01_dataset_samples()
%FIG01_DATASET_SAMPLES Show representative images with contour overlays.

paths = project_paths();
datasets = ["busi", "cvc"];
displayNames = ["BUSI", "CVC-ClinicDB"];
splitFiles = ["busi_seed2981_val.txt", "cvc_seed2981_val.txt"];

samples = strings(2, 2);
ratios = zeros(2, 2);
for datasetIndex = 1:2
    ids = read_id_list(fullfile(paths.splits, splitFiles(datasetIndex)));
    maskRatios = zeros(numel(ids), 1);
    for sampleIndex = 1:numel(ids)
        [~, maskPath] = sample_paths(datasets(datasetIndex), ids(sampleIndex));
        mask = read_binary_mask(maskPath);
        maskRatios(sampleIndex) = mean(mask(:));
    end
    quantileTargets = quantile(maskRatios, [0.25, 0.75]);
    for sampleIndex = 1:2
        [~, selectedIndex] = min(abs(maskRatios - quantileTargets(sampleIndex)));
        samples(datasetIndex, sampleIndex) = ids(selectedIndex);
        ratios(datasetIndex, sampleIndex) = maskRatios(selectedIndex);
    end
end

fig = new_result_figure(1750, 900);
layout = tiledlayout(fig, 2, 4, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, 'BUSI 与 CVC-ClinicDB 代表性样本及专家轮廓', ...
    'FontSize', 18, 'FontWeight', 'bold');

for datasetIndex = 1:2
    for sampleIndex = 1:2
        dataset = datasets(datasetIndex);
        sampleId = samples(datasetIndex, sampleIndex);
        [imagePath, maskPath] = sample_paths(dataset, sampleId);
        image = imread(imagePath);
        mask = read_binary_mask(maskPath, [size(image, 1), size(image, 2)]);
        overlay = overlay_mask_contour(image, mask, [0.05, 0.92, 0.38], 2);

        nexttile;
        imshow(image);
        title(sprintf('%s / %s\n原图', displayNames(datasetIndex), sampleId), ...
            'Interpreter', 'none', 'FontSize', 10);

        nexttile;
        imshow(overlay);
        title(sprintf('专家轮廓叠加（前景占比 %.3f）', ...
            ratios(datasetIndex, sampleIndex)), 'FontSize', 10);
    end
end

audit = table( ...
    repelem(datasets', 2), ...
    reshape(samples', [], 1), ...
    reshape(ratios', [], 1), ...
    'VariableNames', {'dataset', 'sample_id', 'mask_ratio'});
writetable(audit, fullfile(paths.output, 'fig01_selected_samples.csv'));

export_result_figure(fig, "fig01_dataset_samples_matlab");
end
