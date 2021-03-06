<!-- badges -->
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jnareb/git-commit-graph-ext/master)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/jnareb/git-commit-graph-ext)

# Commit graph labeling for speeding up Git commands
> Explore possible extensions to the serialized commit-graph format in Git, including adding reachability indexes for the graph of revisions

Git uses various clever methods for making operations on very large
repositories faster, from bitmap indices for `git fetch`[[1][]], to generation
numbers (also known as topological levels) in the commit-graph file for
commit graph traversal operations like `git log --graph`[[2][]].

The goal of this project is to examine various possible improvements that
can make Git even faster, other than just using generation numbers.
For example there are many methods to make reachability queries in very large graphs
faster; it remains to be seen if they would work on large commit graphs
(the graph of project history) as well as they work on other real-life graphs.

Ultimately, this project is about examining extension to Git's [commit-graph][]
feature, including mainly adding reachability indexes / labels
for the DAG (Directed Acyclic Graph) of revisions.

[1]: https://githubengineering.com/counting-objects/ "Counting Objects | The GitHub Blog"
[2]: https://devblogs.microsoft.com/devops/supercharging-the-git-commit-graph-iii-generations/ "Supercharging the Git Commit Graph III: Generations and Graph Algorithms | Azure DevOps Blog"
[commit-graph]: https://git-scm.com/docs/commit-graph

----

This project, while mainly exploratory in nature, is using [`nbdev`][nbdev] library for literate programming in Python using Jupyter Notebooks -- not to create a Python module (to publish in PyPi and/or Conda), but to allow for splitting it up.

The original notebook at Google Colaboratory: "[Reachability labels for version control graphs.ipynb][colab-1]" got quite unwieldy; it takes too much time to run it.  By splitting it into smaller notebooks, and turning the code into helper modules, the hope is that it should be possible to quickly go to the interesting parts of exploration.

[nbdev]: https://nbdev.fast.ai/ "nbdev - Create delightful Python projects using Jupyter Notebooks"
[colab-1]: https://colab.research.google.com/drive/1V-U7_slu5Z3s5iEEMFKhLXtaxSu5xyzg "Reachability labels for version control graphs.ipynb | Colaboratory"

## Graph operations in Git

This project focuses on the Git operations that involve examining and walking the commit graph, i.e. the project history.
Such operations include:

 - `git merge-base --is-ancestor`
 - `git branch --contains`
 - `git tag --contains`
 - `git branch --merged`
 - `git tag --merged`
 - `git merge-base --all`
 - `git log --topo-sort`
 
Only the first command performs straight reachability query.

## Table of contents

> Warning: this is not generated automatically

1. [Graphs in Python](01_tools.ipynb)
2. [Related works: various reachability labellings](02_related.ipynb)
3. [Example directed graphs](03_example_graphs.ipynb)
4. Drawing graphs
5. [Reachability index](05_reachability_index.ipynb)
6. [Topological levels](06_levels.ipynb)
7. [DFS intervals labelling](07_interval_labels.ipynb)
8. [Reachability queries](08_reach.ipynb)
9. [Extracting commit graphs from Git repositories](09_git.ipynb)
10. [Checkpointing](10_checkpoint.ipynb)
11. [Graph datasets](11_datasets.ipynb)
12. [Large Git repositories](12_repos.ipynb)
13. Graph stats
14. [Reachability evaluation](14_evaluation.ipynb)

## Slides

This topic is covered in much more details in slides for the presentation "[_Graph operations in Git version control system_][google-drive-slides]" by Jakub Narebski (2019).

Those slides are also available to read on SlideShare and on Speaker Deck:

- <https://www.slideshare.net/JakubNarbski/graph-operations-in-git-version-control-system-how-the-performance-was-improved-for-large-repositories-how-can-it-be-further-improved>
- <https://speakerdeck.com/jnareb/graph-operations-in-git-and-how-to-make-them-faster>

[google-drive-slides]: https://drive.google.com/open?id=1psMBVfcRHcZeJ7AewGpdoymrEfFVdXoK "Graph operations in Git version control system (PDF)"

## TODO: Notebooks to split

- [ ] [Reachability labels for version control graphs](Reachability_labels_for_version_control_graphs.ipynb) (doing)
- [x] [Reachability queries in large graphs](Reachability_queries_in_large_graphs.ipynb) (done)
