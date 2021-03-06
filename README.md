# callipy: call IPython notebooks with arguments

## Dependencies

- `runipy`: https://github.com/paulgb/runipy
- `IPython` (tested with IPython 2.3.0)

## Installation

```
pip install callipy
```

## Simple Usage

Let's create a notebook called `notebook.ipynb`, containing the following cell:

```python
y = 2 * x
```

Now let's call this notebook from another session with a value for `x` and get the result `y`:

```python
>>> import callipy
>>> callipy.call_notebook("notebook.ipynb", x=2).y
4
```

## How it works

First the keyword arguments given to `call_notebook` are injected into the notebook's namespace and `runipy` is used to execute all of its cells:

```python
>>> result = callipy.call_notebook("notebook.ipynb", x=2)
>>> result
<callipy.NotebookResult at 0x106b92f10>
```

After running the notebook, the value of any variable in the notebook's namespace can be read using attribute or dict notation:

```python
>>> result.y
4
>>> result['y']
4
```

Note: arguments and output values must be pickleable.

Finally, the notebook object itself can be accessed as `result.notebook`. See https://github.com/paulgb/runipy for examples of things you can do with the notebook object.

## Default values and validation

That's all good and well, but we have a slight problem: if we try to run the target notebook on its own, it will complain about `x` not being defined.

The solution is to declare the parameters and their default value at the beginning of `notebook.ipynb`:

```python
%load_ext callipy
%param x 5
```

Now we can run the notebook from the browser, or call it without arguments, and it will use the default value for every missing argument:

```python
>>> callipy.call_notebook("notebook.ipynb").y
10
```

When more than one value is given, the parameter behaves as an enumerated type and the first value is the default value:

```python
%param mode "simple", "advanced"
```

If the notebook is called with a value that was not declared, an error will be raised:

```python
>>> callipy.call_notebook("notebook.ipynb", mode="wrong")
ValueError: Invalid value 'wrong' for parameter mode: "simple", "advanced"
```

You can customise this behaviour by giving as the default value an object `mydefault` that supports the following:

- `mydefault[0]`: returns the default value
- `mydefault[param_name]`: as above, but with the parameter name
- `x in mydefault`: tests whether `x` is allowed

Note that a lone string is treated as an atomic value, not as an enumeration of characters:

```python
%param a "test" # the default value is 'test'
%param b list("test") # the default value is 't'
```

Finally, a notebook can be queried for the parameters it declares:

```python
>>> callipy.get_notebook_params("notebook.ipynb")
{'x': 5, 'mode': ("simple", "advanced")}
```

Caveat: to extract this information, `callipy` must execute the notebook. What if this takes time or produces side-effects? To alleviate the problem, the instruction `%params_done` can be placed in the notebook:

```python
%param x 5
%param mode "simple", "advanced"
%params_done
```

Then when calling `get_notebook_params()` anything after this cell will be ignored.

## Acknowledgments

Based on the good work by **@paulgb**: https://github.com/paulgb/runipy

Any reference to a famous statue is purely coincidental.