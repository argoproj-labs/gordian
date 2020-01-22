import setuptools

setup_reqs = ["pytest-cov", "pytest-runner", "flake8"]
setuptools.setup(
    name="gordian",
    version="1.1.0",
    author="Intuit",
    author_email="cg-sre@intuit.com",
    description="A tool to search and replace YAML files in a Git repo",
    url="https://github.com/argoproj-labs/gordian",
    install_requires=['pygithub', 'pyyaml', 'jsonpatch', 'deepdiff'],
    setup_requires=setup_reqs,
    extras_require={
        'test': setup_reqs
    },
    tests_require=setup_reqs,
    packages=["gordian"],
    entry_points={
        'console_scripts': [
            'gordian = gordian.gordian:main',
            'pulpo = gordian.pulpo:main',
        ],
    },
)
