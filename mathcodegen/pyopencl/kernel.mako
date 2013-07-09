__kernel void map(
% for i in range(len(arrays)):
% if i < len(arrays) - 1:
    __global float* ${arrays[i][0]},
% else:
    __global float* ${arrays[i][0]}) {
% endif
% endfor
unsigned int i = get_global_id(0);
% if iterations > 1:
for (int it = 0; it < ${iterations}; ++it) {
% endif
% for out, res in zip(output, result):
${out} ${assignment} ${res};
% endfor
% if iterations > 1:
}
% endif
}
