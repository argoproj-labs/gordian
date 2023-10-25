import setuptools
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup_reqs = ["pytest", "pytest-cov", "pytest-runner", "flake8"]
setuptools.setup(
    name="gordian",
    version="3.7.0",
    author="Intuit",
    author_email="cg-sre@intuit.com",
    description="A tool to search and replace files in a Git repo",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/argoproj-labs/gordian",
    install_requires=["pygithub<2.0.0", "pyyaml", "jsonpatch", "deepdiff", "retry"],
    setup_requires=setup_reqs,
    extras_require={"test": setup_reqs},
    tests_require=setup_reqs,
    packages=["gordian", "gordian.files"],
    entry_points={
        "console_scripts": [
            "gordian = gordian.gordian:main",
            "pulpo = gordian.pulpo:main",
        ],
    },
)
