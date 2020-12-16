FROM gitpod/workspace-full

# Install custom tools, runtimes, etc.
# For example "bastet", a command-line tetris clone:
# RUN brew install bastet
#
# More information: https://www.gitpod.io/docs/config-docker/
RUN pip install --upgrade pip
RUN pip install nbdev
RUN pip install networkx
RUN pip install matplotlib
RUN pip install seaborn
RUN pip install pandas
RUN pip install tables
CD /workspace/git-commit-graph-ext
RUN nbdev_install_git_hooks
# Jekyll for GitHub Pages
RUN sudo apt-get install ruby-full build-essential zlib1g-dev
RUN gem install jekyll bundler
RUN cd docs && bundle install
