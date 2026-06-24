function paths = project_paths()
%PROJECT_PATHS Return stable absolute paths used by all MATLAB figures.

scriptDir = fileparts(mfilename('fullpath'));
paths.script = scriptDir;
paths.root = fileparts(scriptDir);
paths.output = fullfile(scriptDir, 'output');
paths.tables = fullfile(paths.root, 'paper', 'tables');
paths.results = fullfile(paths.root, 'experiments', 'results');
paths.data = fullfile(paths.root, 'data', 'processed');
paths.splits = fullfile(paths.root, 'data', 'splits');

if ~exist(paths.output, 'dir')
    mkdir(paths.output);
end
end
