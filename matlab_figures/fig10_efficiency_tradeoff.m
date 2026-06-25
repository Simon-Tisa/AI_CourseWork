function fig10_efficiency_tradeoff()
%FIG10_EFFICIENCY_TRADEOFF Plot IoU, inference time and parameter count.

paths = project_paths();
results = readtable(fullfile(paths.tables, 'segmentation_results.csv'), ...
    'TextType', 'string');

modelLabels = ["U-Net", "U-KAN(no-KAN)", "U-KAN", "Attention-U-KAN"];
runNames = {
    ["busi_unet_seed2981", "busi_no_kan_seed2981", "busi_ukan_seed2981", "busi_attention_ukan_seed2981"]
    ["cvc_unet_seed2981", "cvc_no_kan_seed2981", "cvc_ukan_seed2981", "cvc_attention_ukan_seed2981"]
};
datasetLabels = ["BUSI", "CVC-ClinicDB"];
colors = lines(4);

fig = new_result_figure(1500, 680);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '模型精度—效率—参数量权衡', ...
    'FontSize', 18, 'FontWeight', 'bold');

for datasetIndex = 1:2
    iou = zeros(4, 1);
    inferenceTime = zeros(4, 1);
    parameters = zeros(4, 1);
    for modelIndex = 1:4
        row = results.name == runNames{datasetIndex}(modelIndex);
        iou(modelIndex) = results.iou(row);
        inferenceTime(modelIndex) = results.infer_ms_per_image(row);
        parameters(modelIndex) = results.params(row);
    end

    ax = nexttile;
    hold(ax, 'on');
    for modelIndex = 1:4
        markerSize = 70 + 18 * parameters(modelIndex) / 1e6;
        scatter(ax, inferenceTime(modelIndex), iou(modelIndex), markerSize, ...
            colors(modelIndex, :), 'filled', ...
            'MarkerFaceAlpha', 0.82, ...
            'MarkerEdgeColor', 'white', ...
            'LineWidth', 1.0);
        text(ax, inferenceTime(modelIndex) * 1.05, iou(modelIndex), ...
            sprintf('%s\n%.2fM', modelLabels(modelIndex), parameters(modelIndex) / 1e6), ...
            'FontSize', 9, 'VerticalAlignment', 'middle');
    end
    hold(ax, 'off');
    set(ax, 'XScale', 'log');
    xlim(ax, [2.5, 70]);
    ylim(ax, [min(iou) - 0.025, max(iou) + 0.025]);
    grid(ax, 'on');
    ax.GridAlpha = 0.17;
    xlabel(ax, '单图推理时间（ms，对数坐标）');
    ylabel(ax, 'IoU');
    title(ax, datasetLabels(datasetIndex));
end

export_result_figure(fig, "fig10_efficiency_tradeoff_matlab");
end
