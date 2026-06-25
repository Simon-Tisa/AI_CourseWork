function plot_prediction_dataset(dataset, outputBaseName)
%PLOT_PREDICTION_DATASET Compare U-KAN and Attention-U-KAN predictions.

paths = project_paths();
dataset = lower(string(dataset));
if dataset == "busi"
    splitFile = 'busi_seed2981_val.txt';
    ukanRun = "busi_ukan_seed2981";
    attentionRun = "busi_attention_ukan_seed2981";
    datasetLabel = "BUSI";
else
    splitFile = 'cvc_seed2981_val.txt';
    ukanRun = "cvc_ukan_seed2981";
    attentionRun = "cvc_attention_ukan_seed2981";
    datasetLabel = "CVC-ClinicDB";
end

ids = read_id_list(fullfile(paths.splits, splitFile));
ids = ids(1:4);

fig = new_result_figure(1850, 1450);
layout = tiledlayout(fig, 4, 5, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, datasetLabel + " 验证集预测结果对比", ...
    'FontSize', 18, 'FontWeight', 'bold');
columnTitles = ["原图", "专家标注", "U-KAN", "Attention-U-KAN", "注意力模型误差图"];

for sampleIndex = 1:numel(ids)
    sampleId = ids(sampleIndex);
    [imagePath, maskPath, ukanPath] = sample_paths(dataset, sampleId, ukanRun);
    [~, ~, attentionPath] = sample_paths(dataset, sampleId, attentionRun);

    image = ensure_rgb(imread(imagePath));
    image = imresize(image, [256, 256], 'bilinear');
    groundTruth = read_binary_mask(maskPath, [256, 256]);
    ukanPrediction = read_binary_mask(ukanPath, [256, 256]);
    attentionPrediction = read_binary_mask(attentionPath, [256, 256]);
    errorMap = prediction_error_rgb(groundTruth, attentionPrediction);

    panels = {image, groundTruth, ukanPrediction, attentionPrediction, errorMap};
    for columnIndex = 1:5
        nexttile;
        imshow(panels{columnIndex});
        if sampleIndex == 1
            title(columnTitles(columnIndex), 'FontSize', 10);
        end
        if columnIndex == 1
            ylabel(sampleId, 'Interpreter', 'none', 'FontWeight', 'bold');
        end
    end
end

annotation(fig, 'textbox', [0.15, 0.005, 0.7, 0.03], ...
    'String', '误差图：绿色=正确前景，红色=过分割，蓝色=漏分割', ...
    'EdgeColor', 'none', 'HorizontalAlignment', 'center', 'FontSize', 10);

export_result_figure(fig, outputBaseName);
end
