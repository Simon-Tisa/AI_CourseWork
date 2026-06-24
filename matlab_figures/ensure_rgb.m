function image = ensure_rgb(image)
%ENSURE_RGB Convert grayscale or RGBA image data to RGB.

if ndims(image) == 2
    image = repmat(image, 1, 1, 3);
elseif size(image, 3) > 3
    image = image(:, :, 1:3);
end
end
