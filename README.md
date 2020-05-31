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

We must also give the observer the dispatcher's address, so the observer may send it messages. When you start the repository observer, you can pass in the dispatcher's server address using the `--dispatcher-server` command line argument. If you do not pass it in, it will assume the default address of `localhost:8000`

So, you can run the repo observer with:

```bash
python repo_observer.py --repo $TEST_REPO --poll 5 --dispatcher-server localhost:8000
```

> Where $TEST_REPO is an env variable with a full path to the repository

If you want to know the arguments that can be passed to the observer:

```bash
$ python repo_observer.py -h
usage: repo_observer.py [-h] [--dispatcher-server DISPATCHER_SERVER] [--repo REPO] [--poll POLL] [--branch BRANCH]

optional arguments:
  -h, --help            show this help message and exit
  --dispatcher-server DISPATCHER_SERVER
                        dispatcher host:port , by default it uses localhost:8000
  --repo REPO           path to the repository to observe
  --poll POLL           how long to keep polling repository
  --branch BRANCH       which branch to run tests against
```

> This will outline all the available arguments to pass to the CLI

### Dispatcher Server (dispather.py)

Dispatcher Server is used to distribute commit to test runners and communicate back test results once test runners
complete running given tests against the given commit. It contains a list of runners & a key value pair of dispatched commits
as well as pending commits.

It uses a custom TCP Server from socket server builtin library which allows spawning of new threads to handle multiple connections. Since the default TCP connection does not allow for handling multple requests, this allows the Dispatcher Server
to spin up new threads whenever a new connection request comes in from either the repository observer or from any of the test runners.

It handles several commands, most are listed in the dispatch_handler.py source code, but in summary here they are:

1. _status_

    This is used to check the status of the dispatcher server

2. _register_

    This is used to register any new test runner. Test runners register themselves with the Dispatch server.

3. _dispatch_

    This is used to dispatch any new commit_ids to the test runners as recevied from the repo observer

4. _results_

    This is used by test runners to communicate results of running tests against the given commit_id
