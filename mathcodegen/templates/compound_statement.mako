({
% for name, subexpression in subexpressions:
${dtype} ${name} = ${subexpression};
% endfor
${expression};
})
