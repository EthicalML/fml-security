# Example Project MLOps Project

A short description of the project.

## Usage

You can get started by installing the environment with the following commands.

Make sure you have all dependencies set up as outlined in the Dependencies section.

```bash
# Recommended to create new environment
make conda-env-create
conda activate example_project

make install
```

Once you have set up you will have a `poetry.lock` file with all the dependencies for full reproducibility.

You can then run the server locally for a test with the following command:

```
make local-run
```

And then you can send a test request to your deployed ML model runtime with the following command:

```
make local-test-request
```

Finally we can just stop the mlserver process:

```
make local-stop
```

## Security

We can perform relevant security checks for the package by using the commands that we have available.

In order to run the python-specific commands we need to make sure to set up the environment accordingly.

```bash
# Recommended to create new environment
make conda-env-create
conda activate example_project_dev

make install-dev
```

Now we can run some of the base security checks:

```bash
# Check CVEs in any of the dependencies installed
make security-local-dependencies 

# Check for insecure code paths
make security-local-code

# Check for old dependencies
make security-local-dependencies-old 
```

In order to perform the container security scans, it is a pre-requisite to have built the image as below.

```
make docker-build
```

Now we can run the dependency scans on top of these.

```
make security-docker
```

If you want to just run all the security checks at once you can do so with the main command:

```
make security-all
```

## Dependencies

We recommend using the [version manager asdf-vm](https://github.com/asdf-vm/asdf) for simpler installation of all required command-line dependencies used in this project for development, testing, security, etc.

Once you have set up corretly asdf-vm, you can install all relevant dependencies by running the following:

```
make install-dev-deps
```

In order to install the package you will need to use the [Poetry dependency manager](https://github.com/python-poetry/poetry).



## Project Organization

```
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── docs
│   ├── Makefile
│   ├── commands.rst
│   ├── conf.py
│   ├── examples
│   │   └── model-settings.json
│   ├── getting-started.rst
│   ├── index.rst
│   └── make.bat
├── file
├── example_project
│   ├── __init__.py
│   ├── common.py
│   ├── runtime.py
│   └── version.py
├── pyproject.toml
├── requirements-dev.txt
├── setup.py
└── tests
    ├── conftest.py
    └── test_runtime.py
```


--------

<p><small>Project based on the <a target="_blank" href="https://github.com/EthicalML/sml-security">Secure Production MLOps Cookiecutter</a>. #cookiecuttermlops</small></p>
