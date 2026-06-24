function fig11_metric_heatmap()
%FIG11_METRIC_HEATMAP Plot all five evaluation metrics as heatmaps.

paths = project_paths();
results = readtable(fullfile(paths.tables, 'segmentation_results.csv'), ...
    'TextType', 'string');

modelLabels = ["U-Net", "U-KAN(no-KAN)", "U-KAN", "Attention-U-KAN"];
metricLabels = ["IoU", "Dice", "Precision", "Recall", "Specificity"];
runNames = {
    ["busi_unet_seed2981", "busi_no_kan_seed2981", "busi_ukan_seed2981", "busi_attention_ukan_seed2981"]
    ["cvc_unet_seed2981", "cvc_no_kan_seed2981", "cvc_ukan_seed2981", "cvc_attention_ukan_seed2981"]
};
datasetLabels = ["BUSI", "CVC-ClinicDB"];

fig = new_paper_figure(1650, 720);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '主实验完整评价指标热力图', ...
    'FontSize', 18, 'FontWeight', 'bold');

for datasetIndex = 1:2
    values = zeros(4, 5);
    for modelIndex = 1:4
        row = results.name == runNames{datasetIndex}(modelIndex);
        values(modelIndex, :) = [ ...
            results.iou(row), ...
            results.dice(row), ...
            results.precision(row), ...
            results.recall(row), ...
            results.specificity(row)];
    end

    ax = nexttile;
    imagesc(ax, values);
    colormap(ax, parula(256));
    clim(ax, [0.60, 1.00]);
    axis(ax, 'tight');
    xticks(ax, 1:5);
    xticklabels(ax, metricLabels);
    xtickangle(ax, 18);
    yticks(ax, 1:4);
    yticklabels(ax, modelLabels);
    title(ax, datasetLabels(datasetIndex));
    if datasetIndex == 2
        colorbar(ax, 'Location', 'eastoutside');
    end

    for row = 1:size(values, 1)
        for column = 1:size(values, 2)
            if values(row, column) < 0.79
                textColor = 'white';
            else
                textColor = 'black';
            end
            text(ax, column, row, sprintf('%.4f', values(row, column)), ...
                'HorizontalAlignment', 'center', ...
                'VerticalAlignment', 'middle', ...
                'FontWeight', 'bold', ...
                'Color', textColor, ...
                'FontSize', 9);
        end
    end
end

export_paper_figure(fig, "fig11_metric_heatmap_matlab");
end
