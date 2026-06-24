function mask = read_binary_mask(path, targetSize)
%READ_BINARY_MASK Read a label image and return a logical mask.

mask = imread(path);
if ndims(mask) == 3
    mask = mask(:, :, 1);
end
mask = mask >= 128;
if nargin >= 2 && ~isequal(size(mask), targetSize)
    mask = resize_mask_opencv_nearest(mask, targetSize);
end
end
