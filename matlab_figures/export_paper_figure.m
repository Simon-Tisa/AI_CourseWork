function export_paper_figure(fig, baseName)
%EXPORT_PAPER_FIGURE Export a figure as 300 DPI PNG and vector PDF.

paths = project_paths();
pngPath = fullfile(paths.output, baseName + ".png");
pdfPath = fullfile(paths.output, baseName + ".pdf");

drawnow;
exportgraphics(fig, pngPath, 'Resolution', 300, 'BackgroundColor', 'white');
exportgraphics(fig, pdfPath, 'ContentType', 'vector', 'BackgroundColor', 'white');
close(fig);

fprintf('wrote_png=%s\n', pngPath);
fprintf('wrote_pdf=%s\n', pdfPath);
end
