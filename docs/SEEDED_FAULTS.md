# Seeded faults — Exercises 1 and 2

## Exercise 1: test written before feature

Claude Code invoked `/new-feature cnt_roll_3` against NRP `qwen3`.
The first turn stopped after adding the test and observing the missing-column failure.
The next commit implements the feature. Exact `make test` output:

```text
        --------
        >>> unique_index = pd.Index(list("abc"))
        >>> unique_index.get_loc("b")
        1
    
        >>> monotonic_index = pd.Index(list("abbc"))
        >>> monotonic_index.get_loc("b")
        slice(1, 3, None)
    
        >>> non_monotonic_index = pd.Index(list("abcb"))
        >>> non_monotonic_index.get_loc("b")
        array([False,  True, False,  True])
        """
        casted_key = self._maybe_cast_indexer(key)
        try:
            return self._engine.get_loc(casted_key)
        except KeyError as err:
            if isinstance(casted_key, slice) or (
                isinstance(casted_key, abc.Iterable)
                and any(isinstance(x, slice) for x in casted_key)
            ):
                raise InvalidIndexError(key) from err
>           raise KeyError(key) from err
E           KeyError: 'cnt_roll_3'

../../work/venv/lib/python3.13/site-packages/pandas/core/indexes/base.py:3648: KeyError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_roll_3_excludes_today - KeyError: 'cnt_rol...
1 failed, 15 passed in 2.56s
make: *** [test] Error 1

```
