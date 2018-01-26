# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Operations for working with string Tensors.

See the @{$python/string_ops} guide.

@@string_to_hash_bucket_fast
@@string_to_hash_bucket_strong
@@string_to_hash_bucket
@@reduce_join
@@string_join
@@string_split
@@substr
@@as_string
@@encode_base64
@@decode_base64
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.framework import sparse_tensor
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import gen_string_ops
from tensorflow.python.ops import math_ops

# go/tf-wildcard-import
# pylint: disable=wildcard-import
from tensorflow.python.ops.gen_string_ops import *
from tensorflow.python.util import deprecation
# pylint: enable=wildcard-import


def string_split(source, delimiter=" ", skip_empty=True):  # pylint: disable=invalid-name
  """Split elements of `source` based on `delimiter` into a `SparseTensor`.

  Let N be the size of source (typically N will be the batch size). Split each
  element of `source` based on `delimiter` and return a `SparseTensor`
  containing the split tokens. Empty tokens are ignored.

  If `delimiter` is an empty string, each element of the `source` is split
  into individual strings, each containing one byte. (This includes splitting
  multibyte sequences of UTF-8.) If delimiter contains multiple bytes, it is
  treated as a set of delimiters with each considered a potential split point.

  For example:
  N = 2, source[0] is 'hello world' and source[1] is 'a b c', then the output
  will be

  st.indices = [0, 0;
                0, 1;
                1, 0;
                1, 1;
                1, 2]
  st.shape = [2, 3]
  st.values = ['hello', 'world', 'a', 'b', 'c']

  Args:
    source: `1-D` string `Tensor`, the strings to split.
    delimiter: `0-D` string `Tensor`, the delimiter character, the string should
      be length 0 or 1.
    skip_empty: A `bool`. If `True`, skip the empty strings from the result.

  Raises:
    ValueError: If delimiter is not a string.

  Returns:
    A `SparseTensor` of rank `2`, the strings split according to the delimiter.
    The first column of the indices corresponds to the row in `source` and the
    second column corresponds to the index of the split component in this row.
  """
  delimiter = ops.convert_to_tensor(delimiter, dtype=dtypes.string)
  source = ops.convert_to_tensor(source, dtype=dtypes.string)

  # pylint: disable=protected-access
  indices, values, shape = gen_string_ops._string_split(
      source, delimiter=delimiter, skip_empty=skip_empty)
  # pylint: enable=protected-access
  indices.set_shape([None, 2])
  values.set_shape([None])
  shape.set_shape([2])
  return sparse_tensor.SparseTensor(indices, values, shape)


def _reduce_join_reduction_dims(x, axis, reduction_indices):
  """Returns range(rank(x) - 1, 0, -1) if reduction_indices is None."""
  # TODO(aselle): Remove this after deprecation
  if reduction_indices is not None:
    if axis is not None:
      raise ValueError("Can't specify both 'axis' and 'reduction_indices'.")
    axis = reduction_indices
  if axis is not None:
    return axis
  else:
    # Fast path: avoid creating Rank and Range ops if ndims is known.
    if isinstance(x, ops.Tensor) and x.get_shape().ndims is not None:
      return constant_op.constant(
          np.arange(x.get_shape().ndims - 1, -1, -1), dtype=dtypes.int32)

    # Otherwise, we rely on Range and Rank to do the right thing at run-time.
    return math_ops.range(array_ops.rank(x) - 1, -1, -1)


def reduce_join(inputs, axis=None,
                keep_dims=False,
                separator="",
                name=None,
                reduction_indices=None):
  reduction_indices = _reduce_join_reduction_dims(
      inputs, axis, reduction_indices)
  return gen_string_ops.reduce_join(
      inputs=inputs,
      reduction_indices=reduction_indices,
      keep_dims=keep_dims,
      separator=separator,
      name=name)


reduce_join.__doc__ = deprecation.rewrite_argument_docstring(
    gen_string_ops.reduce_join.__doc__, "reduction_indices", "axis")

ops.NotDifferentiable("StringToHashBucket")
ops.NotDifferentiable("StringToHashBucketFast")
ops.NotDifferentiable("StringToHashBucketStrong")
ops.NotDifferentiable("ReduceJoin")
ops.NotDifferentiable("StringJoin")
ops.NotDifferentiable("StringSplit")
ops.NotDifferentiable("AsString")
ops.NotDifferentiable("EncodeBase64")
ops.NotDifferentiable("DecodeBase64")
