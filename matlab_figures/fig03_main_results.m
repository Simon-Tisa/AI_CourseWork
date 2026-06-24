function fig03_main_results()
%FIG03_MAIN_RESULTS Plot the four-model main results from the result CSV.

paths = project_paths();
results = readtable(fullfile(paths.tables, 'segmentation_results.csv'), ...
    'TextType', 'string');

modelLabels = ["U-Net", "U-KAN(no-KAN)", "U-KAN", "Attention-U-KAN"];
runNames = {
    ["busi_unet_seed2981", "busi_no_kan_seed2981", "busi_ukan_seed2981", "busi_attention_ukan_seed2981"]
    ["cvc_unet_seed2981", "cvc_no_kan_seed2981", "cvc_ukan_seed2981", "cvc_attention_ukan_seed2981"]
};
datasetLabels = ["BUSI", "CVC-ClinicDB"];
colors = [0.16, 0.43, 0.78; 0.96, 0.58, 0.12];

fig = new_paper_figure(1600, 720);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '主实验 IoU 与 Dice 对比（统一 evaluate.py 口径）', ...
    'FontSize', 18, 'FontWeight', 'bold');

for datasetIndex = 1:2
    metrics = zeros(4, 2);
    for modelIndex = 1:4
        row = results.name == runNames{datasetIndex}(modelIndex);
        metrics(modelIndex, :) = [results.iou(row), results.dice(row)];
    end

    ax = nexttile;
    bars = bar(ax, metrics, 'grouped');
    bars(1).FaceColor = colors(1, :);
    bars(2).FaceColor = colors(2, :);
    bars(1).EdgeColor = 'none';
    bars(2).EdgeColor = 'none';
    grid(ax, 'on');
    ax.GridAlpha = 0.15;
    ylim(ax, [0.55, 0.92]);
    ylabel(ax, '指标值');
    title(ax, datasetLabels(datasetIndex));
    xticks(ax, 1:4);
    xticklabels(ax, modelLabels);
    xtickangle(ax, 18);
    legend(ax, {'IoU', 'Dice'}, 'Location', 'southoutside', 'Orientation', 'horizontal');

    for seriesIndex = 1:2
        x = bars(seriesIndex).XEndPoints;
        y = bars(seriesIndex).YEndPoints;
        labels = compose('%.4f', bars(seriesIndex).YData);
        text(ax, x, y + 0.008, labels, ...
            'HorizontalAlignment', 'center', 'FontSize', 9);
    end
end

export_paper_figure(fig, "fig03_main_results_matlab");
end
