from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="linkedin-sourcing-agent",
    version="2.0.0",
    author="Your Name",
    author_email="your-email@example.com",
    description="AI-powered LinkedIn candidate sourcing system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/linkedin-sourcing-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Human Resources",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "linkedin-sourcing=main:enhanced_main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords="linkedin, sourcing, recruitment, hr, ai, automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/linkedin-sourcing-agent/issues",
        "Source": "https://github.com/yourusername/linkedin-sourcing-agent",
        "Documentation": "https://github.com/yourusername/linkedin-sourcing-agent#readme",
    },
) 