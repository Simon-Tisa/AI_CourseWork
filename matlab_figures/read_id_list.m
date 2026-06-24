function ids = read_id_list(path)
%READ_ID_LIST Read non-empty sample identifiers from a split file.

text = fileread(path);
ids = splitlines(string(text));
ids = strtrim(ids);
ids(ids == "") = [];
end
