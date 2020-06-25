import setuptools

setup_reqs = ['pytest', 'pytest-cov', 'pytest-runner', 'flake8']
setuptools.setup(
    name="gordian",
    version="2.1.2",
    author="Intuit",
    author_email="cg-sre@intuit.com",
    description="A tool to search and replace files in a Git repo",
    url="https://github.com/argoproj-labs/gordian",
    install_requires=['pygithub', 'pyyaml', 'jsonpatch', 'deepdiff', 'retry'],
    setup_requires=setup_reqs,
    extras_require={
        'test': setup_reqs
    },
    tests_require=setup_reqs,
    packages=['gordian', 'gordian.files'],
    entry_points={
        'console_scripts': [
            'gordian = gordian.gordian:main',
            'pulpo = gordian.pulpo:main',
        ],
    },
)
