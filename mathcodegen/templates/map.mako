% if iterations > 1:
for (int it = 0; it < ${iterations}; ++it) {
% endif
% for out, res in zip(output, result):
${out[0]} ${assignment} ${res};
% endfor
% if iterations > 1:
}
% endif
