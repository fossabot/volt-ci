# Volt CI

This is a simplified minimal continuous integration (CI) system that demonstrates how typical CI systems work. The assumption here is that you have git installed on your PATH.

## Pre-requisites

A list of some of the things you will need to have on your development environment

### Python 3.5+

Have Python installed on your PATH & preferrably Python 3.5+

### Posix

This uses bash scripts for some of the tasks, so ensure you are running in an environment with POSIX

### Git

Have git installed & on your PATH as the _repo-observer_  will be watching on changes on a sample git repository and will use git commands to run the CI system

## The Architecture

![architecture](./images/architecture.png)

### Repo Observer(repo_observer.py)

The repository observer monitors a repository and notifies the dispatcher when a new commit is seen. In order to work with all version control systems (since not all VCSs have built-in notification systems), this repository observer is written to periodically check the repository for new commits instead of relying on the VCS to notify it that changes have been made. This poll is done every 5 seconds by default, this can be adjusted in the CLI arguments.

The observer will poll the repository periodically, and when a change is seen, it will tell the dispatcher the newest commit ID to run tests against. The observer checks for new commits by finding the current commit ID in its repository, then updates the repository, and lastly, it finds the latest commit ID and compares them. For the purposes of this example, the observer will only dispatch tests against the latest commit. This means that if two commits are made between a periodic check, the observer will only run tests against the latest commit. Usually, a CI system will detect all commits since the last tested commit, and will dispatch test runners for each new commit, but this has been modified for simplicity.

The observer must know which repository to observe. To do this, you can point it to whichever repository. Or can copy the [tests](./tests) directory to any other directory and initialize it i.e.:

```bash
mkdir test_repo
cd test_repo
git init
```

> This will be a master repo. You can name it anything else

While in this directory

``` bash
cp -r tests /path/to/test_repo/
cd /path/to/test_repo
git add tests
git commit -m 'add tests'
```

> Now you have a commit

The observer will use this clone to detect changes. To allow the repository observer to use this clone, we pass it the path when we invoke the repo_observer.py file. The repository observer will use this clone to pull from the main repository.

We must also give the observer the dispatcher's address, so the observer may send it messages. When you start the repository observer, you can pass in the dispatcher's server address using the `--dispatcher-server` command line argument. If you do not pass it in, it will assume the default address of `localhost:8888`
