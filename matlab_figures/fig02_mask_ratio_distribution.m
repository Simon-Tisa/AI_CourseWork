function fig02_mask_ratio_distribution()
%FIG02_MASK_RATIO_DISTRIBUTION Compute mask ratios from every processed mask.

paths = project_paths();
datasets = ["busi", "cvc"];
displayNames = ["BUSI", "CVC-ClinicDB"];
colors = [0.13, 0.42, 0.78; 0.04, 0.58, 0.42];
ratios = cell(1, 2);

for datasetIndex = 1:2
    folder = fullfile(paths.data, datasets(datasetIndex), 'masks', '0');
    files = dir(fullfile(folder, '*.png'));
    values = zeros(numel(files), 1);
    for fileIndex = 1:numel(files)
        mask = read_binary_mask(fullfile(files(fileIndex).folder, files(fileIndex).name));
        values(fileIndex) = mean(mask(:));
    end
    ratios{datasetIndex} = values;
end

fig = new_result_figure(1500, 650);
layout = tiledlayout(fig, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
sgtitle(layout, '全数据集病灶 mask 前景占比分布', 'FontSize', 18, 'FontWeight', 'bold');

edges = 0:0.025:0.50;
for datasetIndex = 1:2
    ax = nexttile;
    histogram(ax, ratios{datasetIndex}, edges, ...
        'FaceColor', colors(datasetIndex, :), ...
        'EdgeColor', 'white', ...
        'FaceAlpha', 0.9);
    hold(ax, 'on');
    meanValue = mean(ratios{datasetIndex});
    medianValue = median(ratios{datasetIndex});
    xline(ax, meanValue, '-', '均值', 'Color', [0.82, 0.18, 0.16], ...
        'LineWidth', 1.8, 'LabelVerticalAlignment', 'middle');
    xline(ax, medianValue, '--', '中位数', 'Color', [0.18, 0.18, 0.18], ...
        'LineWidth', 1.5, 'LabelVerticalAlignment', 'bottom');
    hold(ax, 'off');
    grid(ax, 'on');
    ax.GridAlpha = 0.15;
    xlim(ax, [0, 0.5]);
    xlabel(ax, '前景像素占整幅图像的比例');
    ylabel(ax, '样本数量');
    title(ax, sprintf('%s（n=%d）', displayNames(datasetIndex), numel(ratios{datasetIndex})));
    text(ax, 0.97, 0.93, sprintf('均值 %.4f\n中位数 %.4f', meanValue, medianValue), ...
        'Units', 'normalized', 'HorizontalAlignment', 'right', ...
        'VerticalAlignment', 'top', 'BackgroundColor', 'white', ...
        'EdgeColor', [0.8, 0.8, 0.8], 'Margin', 6);
end

statistics = table(displayNames', ...
    cellfun(@numel, ratios)', ...
    cellfun(@mean, ratios)', ...
    cellfun(@median, ratios)', ...
    'VariableNames', {'dataset', 'sample_count', 'mean_mask_ratio', 'median_mask_ratio'});
writetable(statistics, fullfile(paths.output, 'fig02_mask_ratio_statistics.csv'));

export_result_figure(fig, "fig02_mask_ratio_distribution_matlab");
end
