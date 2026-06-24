function fig = new_paper_figure(width, height)
%NEW_PAPER_FIGURE Create a consistently styled white paper figure.

if nargin < 1
    width = 1600;
end
if nargin < 2
    height = 900;
end

fig = figure( ...
    'Color', 'white', ...
    'Units', 'pixels', ...
    'Position', [80, 80, width, height], ...
    'Renderer', 'painters', ...
    'Visible', 'off');

set(groot, 'defaultAxesFontName', 'Microsoft YaHei');
set(groot, 'defaultTextFontName', 'Microsoft YaHei');
set(groot, 'defaultAxesFontSize', 11);
set(groot, 'defaultAxesLineWidth', 0.8);
set(groot, 'defaultAxesBox', 'off');
set(groot, 'defaultAxesTickDir', 'out');
set(groot, 'defaultLegendBox', 'off');
end
