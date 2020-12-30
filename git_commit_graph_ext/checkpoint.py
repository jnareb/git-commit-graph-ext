# AUTOGENERATED! DO NOT EDIT! File to edit: 10_checkpoint.ipynb (unless otherwise specified).

__all__ = ['graph_to_dataframe', 'dataframe_to_graph', 'guess_format', 'save_df_to_file', 'save_graph_df', 'save_graph',
           'load_df_from_file', 'load_graph_df', 'compute_reachability_labels', 'graph_data_to_dataframe',
           'compute_cached_df', 'compute_cached_graph_df', 'compute_cached_reachability_labels_df',
           'dataframe_to_reachability_labels', 'compute_cached_graph', 'compute_cached_reachability_labels']

# Cell
# creating graphs in Python
import networkx as nx
# checking for existence of paths, and manipulating paths
from pathlib import Path, PurePath
# data analysis and manipulation
import pandas as pd
# reachability labels
from .labelling.levels import find_levels
from .labelling.dfs_intervals import find_dfs_intervals, find_dfs_intervals_extra

# Cell
def _savefile_name(graph_name, out_dir='datasets', kind='df_edgelist', file_format='csv.gz'):
    """Create filename for storing graph structure and other graph data

    This is a helper function used, among others, in ...

    Examples:
    ---------
    >>>> _savefile_name('example_graph')
    Path('datasets/example_graph.df_edgelist.csv.gz')

    Parameters
    ----------
    graph_name : str
        Name of the graph (`<graph>.name` can be used).

    out_dir : str
        Directory where saved commit graph data would be stored.
        Defaults to "datasets".

    kind : str
        What type of data is stored in a file, and in what representation.
        The default value is 'df_edgelist', used to store graph structure in
        the edge list format in a `pandas.DataFrame`.

    file_format : str
        Format of a file, for example how the `DataFrame` is saved.
        Defaults to 'csv.gz' (gzip-compressed Comma Separated Values).

    Returns
    -------
    Path
        Path to the file storing the graph structure or graph data in
        the appropriate representation and appropriate file format.
    """
    # The `out_dir` should not be None
    if out_dir is None:
        out_dir = "."

    # compose the basename of the pathname
    filename = graph_name
    # TODO: there would special case for saving to HDF5 files, which can
    # store multiple data in a single file, so there would be no need
    # to add <kind> to basename of such output file
    if kind is not None and kind != '':
        filename += '.' + kind
    if file_format is not None and file_format != '':
        filename += '.' + file_format
    # generate the name of the output file, as `pathlib.Path` object
    return Path(out_dir) / filename


def _out_basename(graph_name, out_dir='datasets'):
    return _savefile_name(graph_name, out_dir=out_dir, kind=None, file_format=None)



# Cell
def graph_to_dataframe(graph):
    return nx.to_pandas_edgelist(graph)


def dataframe_to_graph(df):
    return nx.from_pandas_edgelist(df, create_using=nx.DiGraph)



# Cell
def guess_format(filename):
    suffixes = PurePath(filename).suffixes
    file_format = suffixes[-1]
    if file_format == '.gz' or file_format == '.txt':
        file_format = suffixes[-2] + file_format
    return file_format[1:]


def save_df_to_file(df, filename, output_format='csv.gz'):
    if output_format is None:
        output_format = guess_format(filename)
    if output_format == 'csv' or output_format == 'csv.gz':
        df.to_csv(filename)
    else:
        raise NotImplementedError("Writing to '{}' format is not supported".format(output_format))


def save_graph_df(df, graph_name, datasets_dir='datasets', output_format='csv.gz', overwrite=False):
    filename = _savefile_name(graph_name, out_dir=datasets_dir,
                              kind='df_edgelist', file_format=output_format)
    print('-> filename:', filename)
    if not overwrite and Path(filename).is_file():
        return
    save_df_to_file(df, filename, output_format=output_format)


def save_graph(graph, graph_name=None, datasets_dir='datasets', output_format='csv.gz', overwrite=False):
    df = graph_to_dataframe(graph)
    # if `graph_name` is not given, check the `name` attribute of the `graph`
    if graph_name is None:
        # NOTE: "'name' in graph" checks if there is node named 'name' in the graph
        if hasattr(graph, 'name'):
            graph_name = graph.name
        else:
            raise RuntimeError("Neither 'graph_name' parameter given, nor 'graph' has 'name' attribute")

    print('-> graph_name:', graph_name)
    save_graph_df(df, graph_name,
                  datasets_dir=datasets_dir, output_format=output_format, overwrite=overwrite)


def load_df_from_file(filename, input_format='csv.gz'):
    if input_format is None:
        input_format = guess_format(filename)
    if input_format == 'csv' or input_format == 'csv.gz':
        return pd.read_csv(filename, index_col=0)
    else:
        raise NotImplementedError("Reading from '{}' format is not supported".format(input_format))


def load_graph_df(graph_name, datasets_dir='datasets', input_format='csv.gz'):
    filename = _savefile_name(graph_name, out_dir=datasets_dir,
                              kind='df_edgelist', file_format=input_format)
    print('<- filename:', filename)
    return load_df_from_file(filename, input_format=input_format)



# Cell
def compute_reachability_labels(graph, recompute=False):
    if recompute or not hasattr(graph, 'lvl'):
        graph.lvl = find_levels(graph)
    if recompute or not hasattr(graph, 'mpi_ext'):
        graph.mpi_ext = find_dfs_intervals_extra(graph)
    return graph



# Cell
def graph_data_to_dataframe(graph, append_to=None):
    compute_reachability_labels(graph)

    # create the DataFrame and name its index
    df = pd.DataFrame.from_dict(graph.mpi_ext, orient='index', columns=['f_min', 'min', 'post'])
    df.index.name = 'node'
    # add other reachability labels
    df['level'] = pd.Series(graph.lvl)
    # add and compute other data
    df['in degree'] = pd.Series(dict(graph.in_degree()))
    df['out degree'] = pd.Series(dict(graph.out_degree()))
    df['degree'] = df['in degree'] + df['out degree']

    # append if needed
    if append_to:
        df = pd.concat([append_to, df], axis=1, join='inner')

    return df



# Cell
def compute_cached_df(code, filename, file_format=None, dont_save=False):
    """Compute `DataFrame`, or retrieve it from a given file if it exists

    Parameters:
    -----------
    code : callable
        Code to call if the `filename` file does not exist.  It should be
        a parameter-less function that returns a `DataFrame`.

    filename : str | Path
        Name of the file that, if exists, stores the `DataFrame`

    file_format : str
        Format of a file, for example how the `DataFrame` is saved.
        Defaults to None (guess from the file name).

    Returns:
    --------
    DataFrame
        Recomputed or loaded from provided file DataFrame.
    """
    if Path(filename).is_file():
        return load_df_from_file(filename, input_format=file_format)
    else:
        df = code()
        if not dont_save:
            save_df_to_file(df, filename, output_format=file_format)
        return df



# Cell
def compute_cached_graph_df(graph_generator, graph_name,
                            datasets_dir='datasets', file_format='csv.gz'):
    filename = _savefile_name(graph_name, out_dir=datasets_dir,
                              kind='df_edgelist', file_format=file_format)
    return compute_cached_df(lambda: graph_to_dataframe(graph_generator()), filename)


def compute_cached_reachability_labels_df(graph, graph_name=None, append_to=None,
                                          datasets_dir='datasets', file_format='csv.gz'):
    # if `graph_name` is not given, check the `name` attribute of the `graph`
    if graph_name is None:
        # NOTE: "'name' in graph" checks if there is node named 'name' in the graph
        if hasattr(graph, 'name'):
            graph_name = graph.name
        else:
            raise RuntimeError("Neither 'graph_name' parameter given, nor 'graph' has 'name' attribute")
    # generate filename to save to
    filename = _savefile_name(graph_name, out_dir=datasets_dir,
                              kind='df_nodedata', file_format=file_format)
    # return computer or retrieved dataframe
    return compute_cached_df(lambda: graph_data_to_dataframe(graph, append_to=append_to), filename)



# Cell
def dataframe_to_reachability_labels(df, graph, recompute=False):
    #print('..dataframe_to_reachability_labels({}, {!r}, {})'.format(type(df), graph, recompute))
    if recompute or not hasattr(graph, 'lvl'):
        #print("...recovering 'level' data")
        graph.lvl = df['level'].to_dict()
    if recompute or not hasattr(graph, 'mpi_ext'):
        #print("...recovering 'mpi_ext' data")
        graph.mpi_ext = df[['f_min', 'min', 'post']].to_dict(orient='index')
    return graph

# Cell
def compute_cached_graph(graph_generator, graph_name, datasets_dir='datasets', file_format='csv.gz'):
    filename = _savefile_name(graph_name, out_dir=datasets_dir,
                              kind='df_edgelist', file_format=file_format)
    # generate graph and edgelist dataframe, and return dataframe
    graph = None
    def generate_graph_df():
        graph = graph_generator()
        graph.df_edgelist = graph_to_dataframe(graph)
        return graph.df_edgelist

    graph_df = compute_cached_df(generate_graph_df, filename)

    # if retrieved from the cache, regenerate graph
    if graph is None:
        graph = dataframe_to_graph(graph_df)
        graph.df_edgelist = graph_df

    if not hasattr(graph, 'name'):
        graph.name = graph_name

    #print('graph_name: {}'.format(graph_name))
    #print('graph.name: {}'.format(graph.name))

    return graph


def compute_cached_reachability_labels(graph, graph_name=None, add_missing_nodes=True,
                                       datasets_dir='datasets', file_format='csv.gz'):
    graph.df_nodedata = compute_cached_reachability_labels_df(graph, graph_name=graph_name,
                                                              datasets_dir=datasets_dir, file_format=file_format)
    dataframe_to_reachability_labels(graph.df_nodedata, graph)
    if add_missing_nodes and set(graph.nodes) < set(graph.df_nodedata.index):
        graph.add_nodes_from(set(graph.df_nodedata.index) - set(graph.nodes))

    return graph
