from setuptools import setup, find_packages

setup(
    name="ai-music-generator",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-login",
        "flask-babel",
        "email-validator",
        "python-dotenv",
        "flask-wtf",
        "werkzeug",
        "pyfluidsynth",
        "mido",
        "numpy",
        "scipy",
        "librosa",
    ],
    python_requires=">=3.8",
) 