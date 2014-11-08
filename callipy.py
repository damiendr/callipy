from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
import cPickle as pickle
import runipy
import ast


@magics_class
class ParameterMagics(Magics):
    def __init__(self, shell):
        super(ParameterMagics, self).__init__(shell)
        self.params = dict()
        self.has_params = False

    @line_magic
    def params_done(self, line):
        self.has_params = True

    @line_magic
    def param(self, line):
        # Parse the line into a parameter name and a parameter spec:
        name, spec_str = line.split(None, 1)
        spec = eval(spec_str, self.shell.user_ns)
        self.params[name] = spec

        # If `spec` is a container, then the default value is
        # the first item and `val in spec` can be used for
        # validation.
        try:
            # Treat lone strings as atoms, not as containers:
            if isinstance(spec, basestring): raise TypeError
            default_value = spec[0]
            allowed_values = spec
        except TypeError:
            # The spec *is* the default value; don't validate.
            default_value = spec
            allowed_values = None

        # Do we already have a value for this parameter?
        if not name in self.shell.user_ns:
            # Nope. Inject the default value into the namespace:
            self.shell.user_ns[name] = default_value
        else:
            # Yes. Validate the existing value against the spec:
            value = self.shell.user_ns[name]
            if allowed_values is not None and value not in allowed_values:
                raise ValueError("Invalid value '%s' for parameter %s: %s" \
                                 % (value, name, spec_str))


def load_ipython_extension(ip):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    magics = ParameterMagics(ip)
    ip.register_magics(magics)


def execute(shell, code):
    shell.execute(code, silent=True)
    reply = shell.get_msg()
    if reply["content"]["status"] != "ok":
        raise Exception(reply["traceback"])


def inject(shell, **vars):
    """ Injects variables read from the given dict into the kernel """
    execute(shell, "import cPickle")

    for name, value in vars.items():
        # We can only pass strings to the kernel, so the value
        # will need to be pickled and unpickled:
        code = '%s = cPickle.loads(r"""%s""")' \
                % (name, pickle.dumps(value, protocol=0))
        execute(shell, code)


def pull(shell, expr):
    """
    Reads the value of the given expression from the kernel.
    """
    execute(shell, "import cPickle")

    # Tell the shell to fetch the pickled variable value:
    pickled_expr = "cPickle.dumps(%s, protocol=0)" % expr
    exprs = dict(expr=pickled_expr)
    shell.execute("pass", user_expressions=exprs, silent=True)

    # Read the reply and unpickle the value:
    reply = shell.get_msg()
    out = reply["content"]["user_expressions"]["expr"]
    if out["status"] == "ok":
        pickled_var = ast.literal_eval(out["data"]["text/plain"])
        return pickle.loads(pickled_var)
    else:
        raise Exception(out["traceback"])


def call_notebook(path, **kwargs):
    from runipy.notebook_runner import NotebookRunner
    from IPython.nbformat.current import read

    # Load the notebook:
    with open(path) as f:
        notebook = read(f, 'json')
    r = NotebookRunner(notebook)

    # Inject the call arguments into the kernel and run the notebook:
    inject(r.shell, **kwargs)
    r.run_notebook()

    # The user might want to read some output values from the kernel:
    class NotebookResult(object):
        notebook = r.nb
        def __getattr__(self, name):
            return pull(r.shell, name)
        def __getitem__(self, name):
            return pull(r.shell, name)
    return NotebookResult()


def get_notebook_params(path):
    from runipy.notebook_runner import NotebookRunner
    from IPython.nbformat.current import read

    # Load the notebook:
    with open(path) as f:
        notebook = read(f, 'json')
    r = NotebookRunner(notebook)

    def callback(cell_idx):
        try:
            # Has the %params_done magic been called yet?
            has_params = pull(r.shell,
                "get_ipython().magics_manager.registry['ParameterMagics']"
                ".has_params")
        except:
            # The magic probably hasn't been loaded yet.
            pass
        else:
            if has_params: raise StopIteration() # Yes, we're done!

    # Run the notebook, checking whether we're done after every cell:
    try: r.run_notebook(progress_callback=callback)
    except StopIteration: pass

    # Pull the param declarations:
    try: params = pull(r.shell,
                "get_ipython().magics_manager.registry['ParameterMagics']"
                ".params")
    except: params = dict()
    return params

