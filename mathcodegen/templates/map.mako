% if iterations > 1:
for (int it = 0; it < ${iterations}; ++it) {
% endif
% for out, res in zip(output, result):
% if not parallel:
for (int i = 0; i < ${out[1]}; ++i) {
% endif
${out[0]} ${assignment} ${res};
% if not parallel:
}
% endif
% endfor
% if iterations > 1:
}
% endif
