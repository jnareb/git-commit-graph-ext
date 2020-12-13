FROM gitpod/workspace-full

# Install custom tools, runtimes, etc.
# For example "bastet", a command-line tetris clone:
# RUN brew install bastet
#
# More information: https://www.gitpod.io/docs/config-docker/
RUN pip install nbdev
RUN pip install networkx
RUN pip install matplotlib
RUN nbdev_install_git_hooks
# Jekyll for GitHub Pages
RUN gem install jekyll bundler
RUN cd docs && bundle install