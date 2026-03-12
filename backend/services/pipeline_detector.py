import os


def detect_project_type(path):
    for root, dirs, files in os.walk(path):

        if "requirements.txt" in files:
            return "python"

        if "package.json" in files:
            return "node"

        if "pom.xml" in files:
            return "java"

        if "Dockerfile" in files:
            return "docker"

    return "unknown"
