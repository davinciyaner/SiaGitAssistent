import os


def write_pipeline(path, pipeline):
    workflow_dir = os.path.join(path, ".github", "workflow")

    os.makedirs(workflow_dir, exist_ok=True)

    file_path = os.path.join(workflow_dir, "ci.yml")

    with open(file_path, "w") as f:
        f.write(pipeline)

    return file_path